
# class AppContext:
#     """"
#     A simple context class to hold shared data across the application.
#     """
#     def __init__(self):
#         # self.config = {}
#         self.shared = {}

#     def add(self, key, value):
#         if not isinstance(key, str) or not key.strip():
#             raise ValueError("Invalid key")
#         self.shared[key.strip().lower()] = value

#     def get(self, key):
#         if not isinstance(key, str) or not key.strip():
#             raise ValueError("Invalid key")
#         return self.shared[key.strip().lower()]

# context = AppContext()
