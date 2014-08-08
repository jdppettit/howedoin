import stripe

stripe.api_key = "sk_test_XyBItKO0iLZssC4uqGCLOOWd"

stripe.Plan.create(
    amount=1000,
    interval='month',
    name='Howedoin Business',
    currency='usd',
    id='business')

stripe.Plan.create(
    amount=2500,
    interval='month',
    name='Howedoin Enterprise',
    currency='usd',
    id='enterprise')

