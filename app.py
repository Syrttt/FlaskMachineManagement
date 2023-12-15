from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=True)

# Fabrika modeli
class Factory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    user = db.relationship('User', backref='factory', lazy=True)


# Makine modeli
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    features = db.Column(db.String(255))
    factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
    factory = db.relationship('Factory', backref='machines', lazy=True)

# Makine özellikleri modeli
class MachineFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    feature_value = db.Column(db.String(255))


# JWT ile kullanıcı girişi
# Login işlemi
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.password == data['password']:
        identity = {'id': user.id, 'user_type': 'admin' if user.factory_id is None else 'normal'}
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

    
# Fabrikayı oluştururken default olarak kullanıcı oluştur
@app.route('/create_factory', methods=['POST'])
@jwt_required()
def create_factory():
    current_user_id = get_jwt_identity()
    user_type = get_jwt_identity().get('user_type', 'normal')

    if user_type == 'admin':
        data = request.get_json()
        factory_name = data.get('factory_name')

        if not factory_name:
            return jsonify({"message": "Factory name is required"}), 400

        new_factory = Factory(name=factory_name)
        db.session.add(new_factory)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error creating factory"}), 500

        # Fabrikaya ait default kullanıcı oluştur
        default_user = User(username=factory_name.lower(), password="default_password", factory=new_factory)
        db.session.add(default_user)

        try:
            db.session.commit()
            return jsonify({"message": "Factory and default user created successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error creating default user"}), 500
    else:
        return jsonify({"message": "Unauthorized"}), 401



# Fabrikaları ve makineleri listeleme
@app.route('/factories', methods=['GET'])
@jwt_required()
def get_factories():
    user_type = get_jwt_identity().get('user_type', 'normal')

    if user_type == 'admin':
        factories = Factory.query.all()
        return jsonify([{"factory_name": factory.name, "machines": [machine.name for machine in factory.machines]} for factory in factories])
    else:
        current_user_id = get_jwt_identity().get('id')
        user = User.query.get(current_user_id)

        if user:
            factory = Factory.query.get(user.factory_id)
            if factory:
                return jsonify({"factory_name": factory.name, "machines": [machine.name for machine in factory.machines]})
            else:
                return jsonify({"message": "Factory not found"}), 404
        else:
            return jsonify({"message": "User not found"}), 404
        
#Fabrikaya Makine ekleme
@app.route('/add_machine', methods=['POST'])
@jwt_required()
def add_machine():
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    data = request.get_json()
    machine_name = data.get('machine_name')
    factory_id = data.get('factory_id')  # Only admin users will specify this field

    if not machine_name:
        return jsonify({"message": "Machine name is required"}), 400

    if user_type == 'admin':
        if not factory_id:
            return jsonify({"message": "Factory ID is required for admin users"}), 400

        factory = Factory.query.get(factory_id)
        if not factory:
            return jsonify({"message": "Factory not found"}), 404

        new_machine = Machine(name=machine_name, factory=factory)
    else:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        factory = Factory.query.get(user.factory_id)
        if not factory:
            return jsonify({"message": "Factory not found"}), 404

        new_machine = Machine(name=machine_name, factory=factory)

    db.session.add(new_machine)

    try:
        db.session.commit()
        return jsonify({"message": "Machine added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding machine"}), 500


# Fabrika güncellemek için endpoint
@app.route('/update_factory/<int:factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    data = request.get_json()
    new_factory_name = data.get('new_factory_name')

    if not new_factory_name:
        return jsonify({"message": "New factory name is required"}), 400

    if user_type == 'admin':
        # Admin can update any factory
        factory = Factory.query.get(factory_id)
        if not factory:
            return jsonify({"message": "Factory not found"}), 404
    else:
        # Normal user can only update their own factory
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        factory = Factory.query.get(user.factory_id)
        if not factory:
            return jsonify({"message": "Factory not found"}), 404

        if factory.id != factory_id:
            return jsonify({"message": "Unauthorized"}), 401

    factory.name = new_factory_name

    try:
        db.session.commit()
        return jsonify({"message": "Factory updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating factory"}), 500
    
    
#Makinenin adını güncelleme(başka özellikler eklenebilir kendisine)
@app.route('/update_machine/<int:machine_id>', methods=['PUT'])
@jwt_required()
def update_machine(machine_id):
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    data = request.get_json()
    new_machine_name = data.get('new_machine_name')

    if not new_machine_name:
        return jsonify({"message": "New machine name is required"}), 400

    machine = Machine.query.get(machine_id)
    if not machine:
        return jsonify({"message": "Machine not found"}), 404

    if user_type == 'admin':
        # Admin tüm makineleri güncelleyebilir
        try:
            machine.name = new_machine_name
            db.session.commit()
            return jsonify({"message": "Machine updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating machine"}), 500
    else:
        # Normal kullanıcılar sadece kendi fabrikalarındaki makineleri güncelleyebilir
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.factory_id != machine.factory_id:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            machine.name = new_machine_name
            db.session.commit()
            return jsonify({"message": "Machine updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating machine"}), 500



# Makineye özellik ekleme endpoint'i
@app.route('/add_machine_feature/<int:machine_id>', methods=['POST'])
@jwt_required()
def add_machine_feature(machine_id):
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    data = request.get_json()
    feature_name = data.get('feature_name')
    feature_value = data.get('feature_value')

    if not feature_name:
        return jsonify({"message": "Feature name is required"}), 400

    if not feature_value:
        return jsonify({"message": "Feature value is required"}), 400

    machine = Machine.query.get(machine_id)
    if not machine:
        return jsonify({"message": "Machine not found"}), 404

    if user_type == 'admin':
        # Admin tüm makinelere özellik ekleyebilir
        try:
            new_machine_feature = MachineFeature(machine_id=machine_id, feature_name=feature_name, feature_value=feature_value)
            db.session.add(new_machine_feature)
            db.session.commit()
            return jsonify({"message": "Machine feature added successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error adding machine feature"}), 500
    else:
        # Normal kullanıcılar sadece kendi fabrikalarındaki makinelere özellik ekleyebilir
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.factory_id != machine.factory_id:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            new_machine_feature = MachineFeature(machine_id=machine_id, feature_name=feature_name, feature_value=feature_value)
            db.session.add(new_machine_feature)
            db.session.commit()
            return jsonify({"message": "Machine feature added successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error adding machine feature"}), 500

#Makinenin sahip olduğu bir özelliği silme
@app.route('/delete_machine_features', methods=['DELETE'])
@jwt_required()
def delete_machine_features():
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    machine_features_ids = request.get_json().get('machine_features')
    if not machine_features_ids:
        return jsonify({"message": "Machine features IDs are required"}), 400

    for machine_feature_id in machine_features_ids:
        machine_feature = MachineFeature.query.get(machine_feature_id)
        if not machine_feature:
            return jsonify({"message": "Machine feature not found"}), 404

        machine = Machine.query.get(machine_feature.machine_id)
        if not machine:
            return jsonify({"message": "Machine not found"}), 404

        if user_type == 'admin':
            # Admin tüm makine özelliklerini silebilir
            try:
                db.session.delete(machine_feature)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": "Error deleting machine feature"}), 500
        else:
            # Normal kullanıcılar sadece kendi fabrikalarındaki makine özelliklerini silebilir
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({"message": "User not found"}), 404

            if user.factory_id != machine.factory_id:
                return jsonify({"message": "Unauthorized"}), 401

            try:
                db.session.delete(machine_feature)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": "Error deleting machine feature"}), 500

    return jsonify({"message": "Machine features deleted successfully"}), 200


#Makinenin sahip olduğu bir özelliğin değerini güncelleme
@app.route('/update_machine_feature_value/<int:machine_feature_id>', methods=['PUT'])
@jwt_required()
def update_machine_feature_value(machine_feature_id):
    current_user_id = get_jwt_identity().get('id')
    user_type = get_jwt_identity().get('user_type', 'normal')

    machine_feature = MachineFeature.query.get(machine_feature_id)
    if not machine_feature:
        return jsonify({"message": "Machine feature not found"}), 404

    machine = Machine.query.get(machine_feature.machine_id)
    if not machine:
        return jsonify({"message": "Machine not found"}), 404

    if user_type == 'admin':
        # Admin tüm makine özelliklerinin değerini değiştirebilir
        try:
            new_value = request.get_json().get('new_value')
            machine_feature.feature_value = new_value
            db.session.commit()
            return jsonify({"message": "Machine feature value updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating machine feature value"}), 500
    else:
        # Normal kullanıcılar sadece kendi fabrikalarındaki makine özelliklerinin değerini değiştirebilir
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.factory_id != machine.factory_id:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            new_value = request.get_json().get('new_value')
            machine_feature.feature_value = new_value
            db.session.commit()
            return jsonify({"message": "Machine feature value updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating machine feature value"}), 500





# Ana uygulamayı çalıştırma
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('site.db'):
            db.create_all()

            # Admin kullanıcısını eklemek için kontrol ekle
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', password='passadm', factory_id=None)
                db.session.add(admin_user)
                db.session.commit()

    app.run(debug=True)