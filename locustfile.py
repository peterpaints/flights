from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):

    access_token = None

    def register(self):
        self.client.post("/users/register",
                         json={
                             "email": "ellenkey@gmail.com",
                             "password": "Password1"
                         })

    def login(self):
        response = self.client.post("/users/login",
                                    json={
                                        "email": "ellenkey@gmail.com",
                                        "password": "Password1"
                                    })
        self.access_token = response.json()['access_token']
        print(self.access_token)

    @task(2)
    def get_flights(self):
        self.client.get("/flights",
                        headers={
                            'Authorization': self.access_token,
                            'content-type': 'application/json'
                        })

    def on_start(self):
        # self.register()
        self.login()

    def on_stop(self):
        pass


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
