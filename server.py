import threading
import mathdb_pb2_grpc
import mathdb_pb2
import grpc
import traceback
from concurrent import futures

class MathCache:
    def __init__(self):
        self.cache = {} # Initiate the Dictionary
        self.cache_order = [] #List to track cache order
        self.max_cache_size = 10 #Max cache size 10
        self.lock = threading.Lock() 

    def Set(self, key, value):
        with self.lock:
            self.cache[key] = value #Set value to the key
            self.cache_order = [] #Set is called so clear cache_order 
    
    def update_cache_order(self,key): #LRU Method
        
        #Conditional to see if key is in cache
        if key in self.cache_order:
            self.cache_order.remove(key)
        self.cache_order.append(key)
        
        #Conditional to see if cache_size > 10
        if len(self.cache_order) > self.max_cache_size:
            key_removed = self.cache_order.pop(0) #Remove from tracking list
            del self.cache[key_removed] #Remove from class object
            
    def Get(self, key):
        with self.lock:
            try:
                value = self.cache[key]
                return value
            except KeyError:
                print("Not existing key")


    def Add(self, key_a, key_b):
        with self.lock: 
            total = self.cache[key_a] + self.cache[key_b]
            
            if ("add", key_a, key_b) not in self.cache_order:
                self.cache[("add", key_a, key_b)] = total
                self.update_cache_order(("add", key_a, key_b))
                return [total, False]
            else:
                self.update_cache_order(("add", key_a, key_b))
                return [total, True]

    def Sub(self, key_a, key_b):
        with self.lock:
            
            difference = self.cache[key_a] - self.cache[key_b]
            
            if ("sub", key_a, key_b) not in self.cache_order:
                self.cache[("sub", key_a, key_b)] = difference
                self.update_cache_order(("sub", key_a, key_b))
                return [difference, False]
            else:
                self.update_cache_order(("sub", key_a, key_b))
                return [difference, True]

    def Mult(self, key_a, key_b):
        with self.lock:
            
            product = self.cache[key_a] * self.cache[key_b]
            
            if ("mult", key_a, key_b) not in self.cache_order:
                self.cache[("mult", key_a, key_b)] = product
                self.update_cache_order(("mult", key_a, key_b))
                return [product, False]
            else:
                self.update_cache_order(("mult", key_a, key_b))
                return [product, True]

    def Div(self, key_a, key_b):
        with self.lock:
            
            quotient = self.cache[key_a] / self.cache[key_b]
            
            if ("div", key_a, key_b) not in self.cache_order:
                self.cache[("div", key_a, key_b)] = quotient
                self.update_cache_order(("div", key_a, key_b))
                return [quotient, False]
            else:
                self.update_cache_order(("div", key_a, key_b))
                return [quotient, True]

class MathDb(mathdb_pb2_grpc.MathDbServicer):
    def __init__(self):
        self.math_cache = MathCache() #Use MathCache to help calculate

        #Override the Six methods in Math Cache
        #Basic Structure from lec/14-grpc-and-compose/final-code/server.py
    def Set(self, request, context):
        try:
            err = "" # err returns empty string when no exceptions
            print(request)
        except Exception:
            err = traceback.format_exc() #traceback.format_exc hint
        self.math_cache.Set(request.key, request.value)
        return mathdb_pb2.SetResponse(error = err)

    def Get(self, request, context):
        err = ""
        try:
            value = self.math_cache.Get(request.key)
            if value !=  None:
                return mathdb_pb2.GetResponse(value = value)
            else:
                err = traceback.format_exc()
                return mathdb_pb2.GetResponse(error = err)
        except Exception:
            err = traceback.format_exc()
            return mathdb_pb2.GetResponse(error = err)

    def Add(self, request, context):
        try:
            err = ""
            add_total, cache_hit = self.math_cache.Add(request.key_a, request.key_b)
            print(request)
        except Exception:
            err = traceback.format_exc()
            return mathdb_pb2.BinaryOpResponse(error = err)
        return mathdb_pb2.BinaryOpResponse(value = add_total, cache_hit = cache_hit, error = err)
    def Sub(self, request, context):
        try:
            err = ""
            sub_diff, cache_hit = self.math_cache.Sub(request.key_a, request.key_b)
            print(request)
        except Exception:
            err = traceback.format_exc()
            return mathdb_pb2.BinaryOpResponse(error = err)
        return mathdb_pb2.BinaryOpResponse(value = sub_diff, cache_hit = cache_hit, error = err)

    def Mult(self, request, context):
        try:
            err = ""
            mult_prod, cache_hit = self.math_cache.Mult(request.key_a, request.key_b)
            print(request)
        except Exception:
            err = traceback.format_exc()
            return mathdb_pb2.BinaryOpResponse(error = err)
        return mathdb_pb2.BinaryOpResponse(value = mult_prod, cache_hit = cache_hit, error = err)

    def Div(self, request, context):
        try:
            err = ""
            div_quo, cache_hit = self.math_cache.Div(request.key_a, request.key_b)
            print(request)
        except Exception:
            err = traceback.format_exc()
            return mathdb_pb2.BinaryOpResponse(error = err)
        return mathdb_pb2.BinaryOpResponse(value = div_quo, cache_hit = cache_hit, error = err)

#Start Server Code Chunk from s24/p3/README.md

if __name__ == "__main__":
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options=(('grpc.so_reuseport', 0),))
  mathdb_pb2_grpc.add_MathDbServicer_to_server(MathDb(), server)
  server.add_insecure_port("[::]:5440", )
  server.start()
  server.wait_for_termination()

