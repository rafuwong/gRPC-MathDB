import mathdb_pb2_grpc, mathdb_pb2
import grpc
import csv
import threading
import sys
from csv import DictReader

hit_count = 0
miss_count = 0
lock = threading.Lock()

def mathdb_process_csv(stub, file_name):
    #math_process_csv loops over the rows in a given csv file_names
    #Access a global variable later protected by lock
    global hit_count
    global miss_count

    #Referenced https://www.geeksforgeeks.org/reading-rows-from-a-csv-file-in-python/ to create basic structure for reading csv
    with open(file_name, 'r', encoding="utf-8") as file_obj:
        reader_obj = DictReader(file_obj) #Was csv_reader but changed to DictReader for debugging help from Jack
        for row in reader_obj:
            operation = row["operation"]
            key_a = row["key_a"]
            key_b = row["key_b"]
            response = None
            #Condtionals for reading command and calling the correct method
            #Format from s24/lec/14-grpc-and-compose/final_code/client.py for reference
            if operation == "set":
                #Change key_b to be the value of the dict at key_a
                val = float(key_b)
                stub.Set(mathdb_pb2.SetRequest(key = key_a, value = val))
                print("set")
            elif operation == "add":
                response = stub.Add(mathdb_pb2.BinaryOpRequest(key_a = key_a, key_b = key_b))

            elif operation == "sub":
                response = stub.Sub(mathdb_pb2.BinaryOpRequest(key_a = key_a, key_b = key_b))

            elif operation == "mult":
                response = stub.Mult(mathdb_pb2.BinaryOpRequest(key_a = key_a, key_b = key_b))

            elif operation == "div":
                response = stub.Div(mathdb_pb2.BinaryOpRequest(key_a = key_a, key_b = key_b))

            #Protect the global variables with a lock
            if operation == "set":
                continue
            with lock:
                if response.cache_hit == True:
                    hit_count += 1
                else:
                    miss_count += 1


def main():
    # use sys to implent argeparse
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <PORT> x1.csv, ...")
        sys.exit(1)
    port = sys.argv[1]
    workloads = sys.argv[2:]
    #Connect to server at the specified port
    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = mathdb_pb2_grpc.MathDbStub(channel)

        #Launch 3 threads each one being responsible for one of the CSVs
        threads = [threading.Thread(target=mathdb_process_csv, args=[stub, w]) for w in workloads] #List comp for each thread for each file
        for t in threads:
            t.start()

        #The main thread should call join to wait until 3 threads are finished
        for t in threads:
            t.join()
    print(hit_count, miss_count)
    #Calculate Hit Rate
    total_req = hit_count + miss_count
    overall_hit_rate = hit_count / total_req

    #print the overall hit rate
    print(f"{overall_hit_rate}")

if __name__ == "__main__":
    main()
