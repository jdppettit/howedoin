import stripe

stripe.api_key = "sk_test_XyBItKO0iLZssC4uqGCLOOWd"

# Don't run this again, should only be run once to make these stripe plans

#stripe.Plan.create(
#    amount=1000,
#    interval='month',
#    name='Howedoin Business',
#    currency='usd',
#    id='business')

#stripe.Plan.create(
#    amount=2500,
#    interval='month',
#    name='Howedoin Enterprise',
#    currency='usd',
#    id='enterprise')

stripe.Plan.create(
    amount=300,
    interval='month',
    name='Howedoin Business - Extra User',
    currency='usd',
    id='business_extra_user')

stripe.Plan.create(
    amount=250,
    interval='month',
    name='Howedoin Enterprise - Extra User',
    currency='usd',
    id='enterprise_extra_user')
