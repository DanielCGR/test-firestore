# %%
# app main file
import restx_monkey as monkey

monkey.patch_restx()

from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
import firebase_admin
from firebase_admin import credentials, firestore
import threading
import os

# %%
# Inicializa Firebase
cred = credentials.Certificate("etc/secrets/firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_name = "items"

# %%
# Inicializa Flask y Flask-RESTPlus
app = Flask(__name__)
api = Api(app, version='1.0', title='API CRUD con Firebase',
            description='Una API CRUD conectada a Firebase Firestore')

# %%
# Define el modelo de datos para Swagger
item_model = api.model('Item', {
    'name': fields.String(required=True, description='El nombre del ítem'),
    'description': fields.String(required=True, description='Descripción del ítem'),
    'price': fields.Float(required=True, description='Precio del ítem')
})

# %%
@api.route('/items')
class ItemList(Resource):
    @api.doc('list_items')
    def get(self):
        """Obtiene todos los items"""
        items_ref = db.collection(collection_name)
        docs = items_ref.stream()
        items = [{doc.id: doc.to_dict()} for doc in docs]
        return jsonify(items)

    @api.expect(item_model)
    @api.doc('create_item')
    def post(self):
        """Crea un nuevo item"""
        data = request.json
        item_ref = db.collection(collection_name).add(data)
        return jsonify({"id": item_ref[1].id}), 201

# %%
@api.route('/items/<string:item_id>')
@api.param('item_id', 'El identificador del item')
class Item(Resource):
    @api.doc('get_item')
    def get(self, item_id):
        """Obtiene un item específico"""
        item_ref = db.collection(collection_name).document(item_id)
        item = item_ref.get()
        if item.exists:
            return jsonify(item.to_dict())
        else:
            return jsonify({"error": "Item not found"}), 404

    @api.expect(item_model)
    @api.doc('update_item')
    def put(self, item_id):
        """Actualiza un item existente"""
        data = request.json
        item_ref = db.collection(collection_name).document(item_id)
        if item_ref.get().exists:
            item_ref.update(data)
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Item not found"}), 404

    @api.doc('delete_item')
    def delete(self, item_id):
        """Elimina un item específico"""
        item_ref = db.collection(collection_name).document(item_id)
        if item_ref.get().exists:
            item_ref.delete()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Item not found"}), 404

# %%


# %%
# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.getenv("PORT", default=5000), debug=False)


