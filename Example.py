from JRecInterface import JRecInterface

print "0"
interface = JRecInterface()
interface.request()
interface.response(True)
interface.request()
interface.response(False)
interface.request()
interface.response(True)

print "1"
# Get Json String
s = interface.recommender_json_str()
# Construct from Json String
interface_t = JRecInterface(recommender_json_str=s)
print interface.user_tag(), interface.user_summary()
print interface_t.user_tag(), interface_t.user_summary()
print "2"


interface = JRecInterface(lang=0)
req = interface.request()
print "Document ID:", req.id
print req.text
print
print "Document ID:", req.id
print req.text
print
print "Document ID:", req.id
print req.text
print

continue_loop = True
while continue_loop:
    while True:
        str = raw_input("Enter user response: yes/no/quit:")
        if str == "yes":
            interface.response(True)
            break
        elif str == "no":
            interface.response(False)
            break
        elif str == "quit":
            continue_loop = False
            break
    if continue_loop:
        req = interface.request()
        print "Document ID:", req.id
        print req.text
        print
