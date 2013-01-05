from google.appengine.ext import db

class Busqueda(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    title = db.StringProperty(required=True, multiline=True)
    pub = db.StringProperty(required=True)
    image = db.StringProperty(required=False)
    def getJson(self):
        return {"id": self.id, "name": self.name, "title": self.title, "image": self.image}
