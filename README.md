# JRec (Fuzzy Partial Ordering Version)

*Required Python Package*
  
  
CaboCha-0.69, MeCab 0.996   
NLTK 3.0.0 (not compatible with newer versions)   pip install -v nltk==3.0.0  
jTransliterate  
enum (for Python 2.7)  
enum34 (Sometimes enum doesn't work)  
requests

<br>
<br>

*Usage*

Initialize:         

`interface = JRecInterface()`

User tag:           

`interface.user_tag()`

User Summary:       

`inferface.user_summary()`

Get a New Article:  

`req = interface.request()`

`req.id`   //Document ID for URL

`req.text` //Text

`req.info` //Extra Info for this Request
                    
User Feedback:      

`interface.response(True or False)`

Get Json String:    

`s = interface.recommender_json_str()`

Construct a new JRecInterface object from Json String:

`interface_t = JRecInterface(recommender_json_str=s)`


<br>
<br>

*See Also: Example.py*
