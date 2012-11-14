import datetime
import unittest

import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, subqueryload, joinedload

import testbase
import testbase
from resources import UserResource, ChatSessionResource, ChatResource
from api import Api

class ResourceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_resource(self):
        #try:
        #    db_session = db_session_factory()
        #    #query = db_session.query(ChatSession).options(subqueryload('users')).join("users").join("chat").filter(User.id.__eq__("11"))
        #    #query = db_session.query(ChatSession).join("chat", "topic").filter(Topic.title=="Web Security")
        #    query = db_session.query(User).join(ChatUser, "chat_session", "chat", "topic",).filter(Topic.title=="Web Security")
        #    print query
        #    for s in query.all():
        #        print s.id
        #finally:
        #    if db_session:
        #        db_session.close()
        
        #query = UserResource.objects.filter(chat_sessions__chat__topic__title="Web Security")
        #print query.query
        #for user in query.all():
        #    print user.first_name
               
        #print UserResource.objects.filter(id=11).all()
        #eastern = pytz.timezone("US/Eastern")
        #query = UserResource.objects.filter(chat_sessions__chat__start=datetime.datetime.now().replace(tzinfo=pytz.utc))
        #print query.query
        #for chat in query.all():
        #    print chat.id

        #for s in  UserResource.objects.get(11).chat_sessions:
        #    print "chat_session_id"
        #    print s.id
        #    if s.chat is not None:
        #        print "chat_id"
        #        print s.chat.id
        #        print "title"
        #        print s.chat.topic.title
        #        print "children"
        #        for t in s.chat.topic.children:
        #            print "child"
        #            print t.title
        #            print t.parent.title
        #    else:
        #        print "bad"
        
        #resource = ChatSessionResource.objects.create(chat_id=1)
        #ChatSessionResource.objects.filter(id=26).update(id=26, token="blah2")
        
        api = Api("api/v1")
        resources = ChatSessionResource.objects.filter(id__in=[3,6]).all()
        resources[0].chat_id = 2
        resources[1].chat_id = 4
        print ChatSessionResource.serializer.serialize(api, resources, "JSON")
        #ChatSessionResource.objects.filter(users__id=11).bulk_update(resources=resources)
        ChatSessionResource.objects.bulk_update(resources=resources)

if __name__ == '__main__':
    unittest.main()
