from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from pymongo import ASCENDING
from flask_restful import Api, Resource
import re

from mongodb_rest_api import mongo, collections, API_KEY

def get_search(db,query,sort):
	data = []
	cursor = db.find(query).sort(sort)
	for item in cursor:
		data.append(item)
	return jsonify({"response":data})

def get_list(db):
	data = []
	cursor = db.find({}).sort([('name',ASCENDING)])
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
	def __init__(self):
		self.collections = collections(self)

	def get(self, category=None, search=None):
		if search:
			query = re.compile(request.args['name'], re.IGNORECASE)

			if search in self.collections:
				return get_search(
					self.collections[search],
					{'name':query},
					[('name',ASCENDING)]
				)

			else:
				return invalid_category(category)

		elif category:
			if category in self.collections:
				return get_list(self.collections[category])

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
				if category in self.collections:
					return post(
						self.collections[category],
						category,
						data.get(category)
					)

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
				if category in self.collections:
					return put(
						self.collections[category],
						category,
						data.get(category)
					)

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
				if category in self.collections:
					return delete(
						self.collections[category],
						category,
						data.get(category)
					)

				else:
					return invalid_category(category)
