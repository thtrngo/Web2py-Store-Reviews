# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    links = [
        dict(
            header= '',
            body= lambda row : \
                A('Buy', \
                    _href=URL('default', 'create_order', args=[row.id]), \
                    _class='btn btn-primary')
                    if auth.user is not None else
                A('Buy', _class='hidden')
        )
    ]
    grid = SQLFORM.grid(
        db.product,
        create=True, 
        editable=True, 
        csv = False, 
        links = links,
    )

    return dict(grid=grid)


def store():
    """Returns the store page, with the list of products to be bought"""
    # Complete.
    links = [
        dict(
            header= '',
            body= lambda row : \
                A('Buy', \
                    _href=URL('default', 'create_order', args=[row.id]), \
                    _class='btn btn-primary')
                    if auth.user is not None else
                A('Buy', _class='hidden')
        )
    ]
    grid = SQLFORM.grid(
        db.product,
        create=True, 
        editable=True, 
        csv = False, 
        links = links,
    )

    return dict(grid=grid)

@auth.requires_login()
def create_order():
    """Page to create an order, accessed from the Buy button."""
    product = db.product(request.args(0))
    profile = db(db.profile.email == auth.user.email).select().first()
    if profile is None:
        redirect(URL('default', 'profile',
                     vars=dict(next=URL('default', 'create_order', args=[product.id]),
                               edit='y')))
    # Ok, here you know the profile exists.
    # Sets the default for the order to be created. 
    db.product_order.product_id.default = product.id
    db.product_order.user.default = auth.user.email
    db.product_order.order_date.default = datetime.datetime.utcnow()
    # Complete.  You have to create a form for inserting an order, and process/return it. 
    return dict(form=form)


@auth.requires_login()
def profile():
    """Page for creating/editing/viewing a profile. 
    It has two modes: edit/create, and view."""
    # This is the email of the user to which the form applies.
    logged_in_profile = db(db.profile.user_email == auth.user.email).select().first()
    in_edit_mode = request.vars.edit == 'y'
    user_email = request.vars.email or auth.user.email
    next_url = request.vars.next
    
    if request.vars.edit == 'y':
        if logged_in_profile is not None:
            title = 'Edit Profile'
            form = SQLFORM(db.profile, logged_in_profile)
        else:
        # Mode for create/edit. 
        # You need to create a form to create (if there is no profile)
        # or edit (if there is a profile) the profile for the user.
            title = 'Create Profile'
            form = SQLFORM(db.profile) 

        if form.process().accepted:
            redirect(request.vars.next or URL('default', 'store'))

    else:
        # Mode for view.
        # You need to read the profile for the user, and return a view form for it, 
        # generated with SQLFORM(db.profile, profile, readonly=True). 
        # You do not need to process the form.
        if logged_in_profile is not None:
            title = 'View Profile'
            form = SQLFORM(db.profile, logged_in_profile, readonly=True)
        else:
            return redirect(URL('default', 'profile', vars=dict(edit='y', next=URL('default', 'profile')))) 
    
    return dict(form=form, title=title)

@auth.requires_login()
def create_order():
    db.product.product_name.readable = db.product.product_name.writable = False
    db.product_order.user_email.readable = db.product_order.user_email.writable = False

    product = db(db.product.id == request.args[0]).select().first()
    db.product_order.order_quantity.requires = IS_INT_IN_RANGE(1, product.product_quantity + 1)

    user = db(db.profile.user_email == auth.user.email).select().first()

    # -------------------- profile redirect code goes here -------------------------
    if user is None:
        return redirect(URL('default', 'profile', vars=dict(edit='y', next=URL('default', 'create_order', args=[product.id]))))
    # -------------------- end of profile redirect code ----------------------------

    form = SQLFORM(db.product_order)
    
    # request.vars contains ONLY the fields that were entered in the SQLFORM (the form on the page)

    db.product_order.product_id.default = product.id
    db.product_order.user_email.default = auth.user.email
    db.product_order.order_date.default = datetime.datetime.utcnow()
    #db.product_order.order_date.readable = False

    if form.validate():
        db.product_order.insert(
            product_id = product.id,
            product_name=db.product.product_name,
            user_email=user.user_email,
            order_quantity=request.vars.order_quantity,
            order_amount_paid = float(request.vars.order_quantity) * product.sales_price
        )
        return redirect(URL('default', 'store'))
    else:
        return dict(form=form, name = product.product_name)

@auth.requires_login()
def order_list():
    """Page to display the list of orders."""
    # Fixes visualization of email and product.  I hope this works, it should give you the idea at least.
    db.product_order.product_id.readable = True
    db.product_order.id.readable = False
    db.product_order.user_email.readable = True
    db.product_order.user_email.represent = lambda v, r : A(v, _href=URL('default', 'profile', vars=dict(email=v)))
    db.product_order.product_id.represent = lambda v, r : A(get_product_name(db.product(v)), _href=URL('default', 'view_product', args=[v]))
    db.product_order.user_email.represent = lambda v, r : \
        A(v, _href=URL('default', 'profile', args=[r.product_id]))

    grid = SQLFORM.grid(
        db.product_order,
        create=False, 
        editable=False, 
        csv = False 
    )
    return dict(grid=grid)


def view_product():
    """Controller to view a product."""
    p = db.product(request.args(0))
    if p is None:
        form = P('No such product')
    else:
        form = SQLFORM(db.product, p, readonly=True)
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


