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

db.define_table('product',
    Field('product_name'),
    Field('product_quantity', 'integer'),
    Field('sales_price', 'float'),
    Field('product_author', 'reference auth_user',default=get_user_id()),
)

db.product.product_author.readable = False

def get_product_name(p):
    return None if p is None else p.product_name

db.product.id.readable = db.product.id.writable = False

db.define_table('profile',
    Field('user_email', default=get_user_email(), readable=False, writable=False),
    Field('user_name', label='Name'),
    Field('user_street', label='Street'),
    Field('user_city', label='City'),
    Field('user_zip_code', 'integer', label='Zip Code'),
)

db.define_table('product_order',
    Field('user_email', default=get_user_email(), readable=False, writable=False),
    #Field('product_name', default=get_product_name, writable = False),
    Field('product_id', label='Product'),
    Field('order_quantity', 'integer', label='Quantity'),
    Field('order_date', 'datetime', default=datetime.datetime.now(), label='Order Date'),
    Field('order_amount_paid', 'float', label='Amount Paid'),
)

db.product_order.product_id.readable = db.product_order.product_id.writable = False
db.product_order.order_date.writable = False
db.product_order.order_amount_paid.writable = False


# after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
