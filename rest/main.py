from google.appengine.ext import ndb
import webapp2
import json

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))  #Allow patch
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

#Homepage for app.
class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("Boats N' Jokes... Guess the joke is on me for poor time management")

#values taken from assignment description
class Slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()
	departure_history = ndb.JsonProperty(repeated=True)

class SlipHandler(webapp2.RequestHandler):
	#get information about slip
	def get(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			if slip:
				slip_dict = slip.to_dict()
				slip_dict['self'] = "/slips/" + id
				self.response.write(json.dumps(slip_dict))
			else:
				self.response.set_status(404)
				return
		else:
			query = Slip.query().fetch()
			slip_array = []
			for slip in query:
				curr_slip= {}
				curr_slip['id'] = slip.id
				curr_slip['number'] = slip.number
				curr_slip['current_boat'] = slip.current_boat
				curr_slip['arrival_date'] = slip.arrival_date
				curr_slip['self'] = '/slips/' + slip.id
				slip_array.append(curr_slip)
				
			self.response.write(json.dumps(slip_array))
	
	#add slip
	def post(self):
		slip_data = json.loads(self.request.body)
		if 'number' in slip_data:
			if slip_data['number']:
				new_slip = Slip(number=slip_data['number'], current_boat= "null")
				new_slip.put()
				new_slip.id = new_slip.key.urlsafe()
				new_slip.put()
				slip_dict = new_slip.to_dict()
				slip_dict['self'] = "/slips/" + new_slip.id
				self.response.write(json.dumps(slip_dict))
				self.response.set_status(201)
			else:
				self.response.set_status(400)
				return
		else:
			self.response.set_status(400)
	
	#delete slip by ID
	def delete(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			if slip:
				if slip.current_boat:
					boat_key = slip.current_boat
					boat = ndb.Key(urlsafe=boat_key).get()
					boat.at_sea = True
					boat.put()
				slip.key.delete()
				self.response.set_status(200)
			else:
				self.response.set_status(404)
				return
		else:
			self.response.set_status(404)
	
	def patch(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			if slip:
				slip_data = json.loads(self.request.body)
				if 'number' in slip_data:
					if slip_data['number']:
						slip.number = slip_data['number']
					else:
						self.response.set_status(400)
						return
				if 'curr_boat' in slip_data:
					if slip.curr_boat:
						old_boat_key = slip.curr_boat
						old_boat = ndb.Key(urlsafe=old_boat_key).get()
						old_boat.at_sea = True
						old_boat.put()
					slip.curr_boat = slip_data['curr_boat']
				if 'arrival_date' in slip_data:
					slip.arrival_date = slip_data['arrival_date']
				slip.put()
			else:
				self.response.set_status(404)
				return
		else:
			self.response.set_status(404)
	
	def put(self, id=None):
		if id:
			slip_data = json.loads(self.request.body)
			if 'number' in slip_data:
				if slip_data['number']:
					slip = ndb.Key(urlsafe=id).get()
					if slip:
						if ('arrival_date' in slip_data and not 'curr_boat' in slip_data) or (not 'arrival_date' in slip_data and 'curr_boat' in slip_data):
							self.reponse.set_status(400)
						else:
							if slip.curr_boat:
								old_boat_key = slip.curr_boat
								old_boat = ndb.Key(urlsafe=old_boat_key).get()
								old_boat.at_sea = True
								old_boat.put()
							if 'arrival_date' in slip_data and 'curr_boat' in slip_data:
								slip.arrival_date = slip_data['arrival_date']
								slip.curr_boat = slip_data['curr_boat']
							else:
								slip.arrival_date = None
								slip.curr_boat = None
							slip.number = slip_data['number']
							slip.departure_history = []
							slip.put()
							self.response.set_status(200)
					else:
						self.response.set_status(404)
						return
				else:
					self.response.set_status(400)
					return
			else:
				self.response.set_status(400)
				return
		else:
			self.response.set_status(404)

#member variables taken from description			
class Boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty()
	length = ndb.IntegerProperty()
	at_sea = ndb.BooleanProperty()

class BoatHandler(webapp2.RequestHandler):
	
	def get(self, id=None):
		if id: #check for ID of specific boat.  
			boat = ndb.Key(urlsafe=id).get()
			if boat:
				boat_dict = boat.to_dict()
				boat_dict['self'] = "/boats/" + id
				self.response.write(json.dumps(boat_dict)) #used to send back boat data
				self.response.set_status(200)
			else:
				self.response.set_status(404)
				return
		else:
			the_boats = Boat.query().fetch()
			boat_list = []
			for boat in the_boats:
				curr_boat= {}
				curr_boat['id'] = boat.id
				curr_boat['name'] = boat.name
				curr_boat['type'] = boat.type
				curr_boat['length'] = boat.length
				curr_boat['at_sea'] = boat.at_sea
				curr_boat['self'] = '/boats/' + boat.id
				boat_list.append(curr_boat)
				
			self.response.write(json.dumps(boat_list))
	
	
	def post(self):
		boat_data = json.loads(self.request.body)
		
		if 'name' in boat_data:
			if boat_data['name']:
				new_boat = Boat(name=boat_data['name'], at_sea=True)
				if 'type' in boat_data:
					new_boat.type = boat_data['type']
				else:
					new_boat.type = None
				if 'length' in boat_data:
					new_boat.length = boat_data['length']
				else:
					new_boat.length = None
				new_boat.put()
				new_boat.id = new_boat.key.urlsafe()
				new_boat.put()
				boat_dict = new_boat.to_dict()
				boat_dict['self'] = "/boats/" + new_boat.id
				self.response.write(json.dumps(boat_dict))
				self.response.set_status(201)
			else:
				self.response.set_status(400)
				return
		else:
			self.response.set_status(400)
	
	def delete(self, id=None):
		if id:
			boat = ndb.Key(urlsafe=id).get()
			if boat:
				if not boat.at_sea:
					query = Slip.query(Slip.current_boat == id)
					slip = query.get()
					slip.current_boat = None
					slip.arrival_date = None
					slip.put()
				boat.key.delete()
				self.response.set_status(200)
			else:
				self.response.set_status(404)
				return
		else:
			self.response.set_status(404)
	
	def patch(self, id=None):
		if id:
			boat = ndb.Key(urlsafe=id).get()
			if boat:
				boat_data = json.loads(self.request.body)
				if 'name' in boat_data:
					if boat_data['name']:
						boat.name = boat_data['name']
					else:
						self.response.set_status(400)
						return
				if  'type' in boat_data:
					boat.type = boat_data['type']
				if 'length' in boat_data:
					boat.length = boat_data['length']
				boat.put()
				self.response.set_status(200)
			else:
				self.response.set_status(404)
				return
		else:
			self.response.set_status(404)
	
	def put(self, id=None):
		if id:
			boat_data = json.loads(self.request.body)
			if 'name' in boat_data:
				if boat_data['name']:
					boat = ndb.Key(urlsafe=id).get()
					if boat:
						if 'name' in boat_data:
							boat.name = boat_data['name']
						else:
							self.response.set_status(400)
							return
						if 'type' in boat_data:
							boat.type = boat_data['type']
						else:
							boat.type = None
						if 'length' in boat_data:
							boat.length = boat_data['length']
						else:
							boat.length = None
						boat.put()
						self.response.set_status(200)
					else:
						self.response.set_status(404)
						return
				else:
					self.response.set_status(400)
					return
			else:
				self.response.set_status(400)
				return
		else:
			self.response.set_status(404)

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/boats', BoatHandler),
	('/boats/(.*)', BoatHandler),
	('/slips', SlipHandler),
	('/slips/(.*)', SlipHandler),
], debug=True)