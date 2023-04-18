from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1,5) #Randomly wait between 1 to 5 seconds.

    @task(2)
    def view_products(self):
        collection_id = randint(2,6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}', 
            name = '/store/products' #This is the tested endpoint
        )
    @task(4)
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(
            f'/store/products/{product_id}',
            name = '/store/products/:id'
            )
    @task(1)
    def add_to_cart(self):
        product_id = randint(1,10)
        self.client.post(
            f'/store/carts/{self.cart_id}/items/',
            name = '/store/carts/items',
            json={
                'product_id': product_id,
                'quantity': 1
            }
        )
    @task
    def say_hello(self):
        self.client.get('/playground/slow_api_call/')
    

    def on_start(self):
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']