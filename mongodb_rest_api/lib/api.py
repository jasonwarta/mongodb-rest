from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from pymongo import ASCENDING
from flask_restful import Api, Resource
import re

from mongodb_rest_api import mongo

API_KEY = "super secret api key"

def get_search(db,query,sort):
	data = []
	cursor = db.find(query).sort(sort)
	for item in cursor:
		data.append(item)
	return jsonify({"response":data})

def get_list(db):
	data = []
	cursor = db.find({}).limit(10).sort([('name',ASCENDING)])
	for item in cursor:
		data.append(item)
	return jsonify({"response":data})

def post(db,name,item):
	if db.find_one({'_id': item['_id']}):
		return {"response": "%s already exists" % name}
	else:
		db.insert(item)
		return {"response": "%s added." % name}

def put(db,name,item):
	if not db.find_one({'_id': item['_id']}):
		return {"response": "%s not found" % name}
	else:
		db.update({'_id': item['_id']}, {'$set': item})
		return {"response": "%s updated." % name}

def delete(db,name,item):
	if not db.find_one({'_id': item['_id']}):
		return {"response": "%s not found" % name}
	else:
		db.remove({'_id': item['_id']})
		return {"response": "%s deleted." % name}

def invalid_category(category):
	return jsonify({"response":"invalid category: %s" % category})


class REST(Resource):
	# list of resources here
	def get(self, category=None, search=None):

		print(category,search)

		if search:
			print("searching: %s" % search)
			
			query = re.compile(request.args['name'], re.IGNORECASE)
			
			if search == 'movie':
				return get_search(mongo.db.movie,{"name":query},[('name',ASCENDING)])

			elif search == 'tv':
				return get_search(mongo.db.tv,{"name": query},[('name',ASCENDING)])
				
			elif search == 'books':
				return get_search(mongo.db.book,{"name": query},[('name',ASCENDING)])
				
			else:
				return invalid_category(category)

		elif category:
			print("listing: %s" % category)

			if category == 'movie':
				return get_list(mongo.db.movie)

			elif category == 'tv':
				return get_list(mongo.db.tv)

			elif category == 'books':
				return get_list(mongo.db.book)
				
			else:
				return invalid_category(category)
		

	def post(self, category=None):
		data = request.get_json()
		if not data or not category:
			data = {"response": "ERROR"}
			return jsonify(data)

		else:
			if data['api-key'] != API_KEY:
				return {"response": "Invalid api key"}

			else:
				if category == 'movie':
					return post(mongo.db.movie,'movie',data.get('movie'))

				elif category == 'tv':
					return post(mongo.db.tv,'tv',data.get('tv'))

				elif category == 'book':
					return post(mongo.db.book,'book',data.get('book'))

				else:
					invalid_category(category)


	def put(self, category=None):
		data = request.get_json()
		if not data or not category:
			return {"response": "ERROR"}

		else:
			if data['api-key'] != API_KEY:
				return {"response": "Invalid api key"}

			else:
				if category == 'movie':
					return put(mongo.db.movie,'movie',data.get('movie'))

				elif category == 'tv':
					return put(mongo.db.tv,'tv',data.get('tv'))

				elif category == 'book':
					return put(mongo.db.book,'book',data.get('book'))

				else:
					return invalid_category(category)


	def delete(self, category=None):
		data = request.get_json()
		if not data or not category:
			return {"response": "ERROR"}

		else:
			if data['api-key'] != API_KEY:
				return {"response": "Invalid api key"}

			else:
				if category == 'movie':
					return delete(mongo.db.movie,'movie',data.get('movie'))

				elif category == 'tv':
					return delete(mongo.db.tv,'tv',data.get('tv'))

				elif category == 'book':
					return delete(mongo.db.book,'book',data.get('book'))

				else:
					return invalid_category(category)
