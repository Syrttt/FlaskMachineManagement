Flask Machine Management Uygulaması

Flask Machine Management Uygulaması
Bu Flask uygulaması, bir makine yönetim sistemini oluşturmak için kullanılan temel bir örnek proje sunmaktadır.
Bu sistemde, fabrikalar, kullanıcılar, makineler ve makinelerin özellikleri üzerinde işlemler gerçekleştirilebilir. 
Ayrıca, kullanıcılar JWT (JSON Web Token) ile kimlik doğrulama yapabilirler.

Kurulum

Python 3'ü bilgisayarınıza indirin ve yükleyin: Python İndirme Sayfası

Gerekli paketleri yüklemek için terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:

"pip install -r requirements.txt"

SQLite veritabanını oluşturmak için terminalde veya komut istemcisinde aşağıdaki komutu çalıştırın:

"python
from app import db
db.create_all()
exit()"


Kullanım

Uygulamayı çalıştırmak için terminal veya komut istemcisinde aşağıdaki komutu kullanın:

"python app.py"

Uygulama ilk çalıştığında veritabanı oluşturur ve bir tane ADMİN kullanıcısı ekler. Admin kullanıcısınn bilgileri username: admin, password: passadm  dir.

Uygulama başladığında, http://127.0.0.1:5000/ adresinden uygulamaya erişebilirsiniz.

Uygulama, aşağıdaki temel endpoint'leri içerir:

/login: Kullanıcı girişi yapmak için POST isteği.
/create_factory: Fabrika ve varsayılan kullanıcıyı oluşturmak için POST isteği (Yalnızca admin kullanıcıları için).
/factories: Fabrikaları ve makineleri listelemek için GET isteği.
/add_machine: Makine eklemek için POST isteği.
/update_factory/<int:factory_id>: Fabrikayı güncellemek için PUT isteği.
/update_machine/<int:machine_id>: Makine adını güncellemek için PUT isteği.
/add_machine_feature/<int:machine_id>: Makineye özellik eklemek için POST isteği.
/delete_machine_features: Makinenin sahip olduğu özellikleri silmek için DELETE isteği.
/update_machine_feature_value/<int:machine_feature_id>: Makinenin sahip olduğu bir özelliğin değerini güncellemek için PUT isteği.
Her endpoint'in kullanımı ve beklenen parametreleri için lütfen ilgili bölümleri ve yorum satırlarını inceleyin.


JWT Kimlik Doğrulama


Tabii ki, işte bu Flask uygulamasına ait genel bir README dosyası örneği:

Flask Machine Management Uygulaması
Bu Flask uygulaması, bir makine yönetim sistemini oluşturmak için kullanılan temel bir örnek proje sunmaktadır. Bu sistemde, fabrikalar, kullanıcılar, makineler ve makinelerin özellikleri üzerinde işlemler gerçekleştirilebilir. Ayrıca, kullanıcılar JWT (JSON Web Token) ile kimlik doğrulama yapabilirler.

Kurulum
Python 3'ü bilgisayarınıza indirin ve yükleyin: Python İndirme Sayfası

Gerekli paketleri yüklemek için terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:

bash
Copy code
pip install -r requirements.txt
SQLite veritabanını oluşturmak için terminalde veya komut istemcisinde aşağıdaki komutu çalıştırın:

bash
Copy code
python
from app import db
db.create_all()
exit()
Kullanım
Uygulamayı çalıştırmak için terminal veya komut istemcisinde aşağıdaki komutu kullanın:

bash
Copy code
python app.py
Uygulama başladığında, http://127.0.0.1:5000/ adresinden uygulamaya erişebilirsiniz.

Uygulama, aşağıdaki temel endpoint'leri içerir:

/login: Kullanıcı girişi yapmak için POST isteği.
/create_factory: Fabrika ve varsayılan kullanıcıyı oluşturmak için POST isteği (Yalnızca admin kullanıcıları için).
/factories: Fabrikaları ve makineleri listelemek için GET isteği.
/add_machine: Makine eklemek için POST isteği.
/update_factory/<int:factory_id>: Fabrikayı güncellemek için PUT isteği.
/update_machine/<int:machine_id>: Makine adını güncellemek için PUT isteği.
/add_machine_feature/<int:machine_id>: Makineye özellik eklemek için POST isteği.
/delete_machine_features: Makinenin sahip olduğu özellikleri silmek için DELETE isteği.
/update_machine_feature_value/<int:machine_feature_id>: Makinenin sahip olduğu bir özelliğin değerini güncellemek için PUT isteği.
Her endpoint'in kullanımı ve beklenen parametreleri için lütfen ilgili bölümleri ve yorum satırlarını inceleyin.



JWT Kimlik Doğrulama


Uygulama, kullanıcıların kimlik doğrulamasını JWT (JSON Web Token) kullanarak gerçekleştirir. 
Kullanıcı girişi yapıldıktan sonra, elde edilen token'ı diğer yetkilendirilmiş endpoint'lerde kullanabilirsiniz.

Her JWT token'ı, kullanıcının kimliğini ve kullanıcı tipini içerir. 
Admin kullanıcılarının tipi "admin" olarak belirlenirken, normal kullanıcıların tipi "normal" olarak belirlenir.

Uygulama, token olmadan veya geçersiz bir token ile erişilen endpoint'lere karşı "Unauthorized" hatası dönecektir.



Veritabanı Yapısı

Uygulama, SQLite veritabanını kullanır. Veritabanı şeması, app.py dosyasında tanımlanan User, Factory, Machine ve MachineFeature modelleri üzerinde oluşturulmuştur.

İlgili modellerin özellikleri ve ilişkileri hakkında daha fazla bilgi için ilgili bölümleri inceleyin.


