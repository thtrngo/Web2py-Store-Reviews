# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime

def get_user_email():
    return None if auth.user is None else auth.user.email

def get_user_id():
    return None if auth.user is None else auth.user.id

def get_name():
    return None if auth.user is None else auth.user.first_name + ' ' + auth.user.last_name

db.define_table('product',
    Field('product_name'),
    Field('product_id'),
    Field('product_description', 'text'),
    Field('product_price', 'float'),
    Field('product_author', 'reference auth_user',default=get_user_id()),
)

db.product.product_author.readable = db.product.product_author.writable = False
db.product.product_id.readable = db.product.product_id.writable = False

db.define_table('star',
    Field('user_email'),
    Field('product_id', 'reference product'),
    Field('rating', 'integer', default = None),
)

db.define_table('review',
    Field('product_id', 'reference product'),
    Field('rating', 'integer', default=0),
    Field('email', default=get_user_email()),
    Field('body', 'text', default=''),
    Field('name', default=get_name()),
)

# after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
