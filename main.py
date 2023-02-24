# 19127449 - Phung Anh Khoa
import os
import redis

# kết nối đến redis
r = redis.Redis(host='localhost', port=6379, db=0)


def printCartDetail(order_id):
    order_details = r.zrange("Cart:" + order_id, 0, -1, withscores=True)
    # In thông tin sản phẩm trong giỏ hàng
    for product in order_details:
        product_id = product[0].decode()
        product_name = r.hget("Product:" + product_id, "name").decode()
        product_price = r.hget("Product:" + product_id, "price").decode()
        product_quantity = product[1]
        print("- Mã sản phẩm: {}, Tên sản phẩm: {}, Giá: {}, Số lượng: {}".format(
            product_id, product_name, product_price, product_quantity))


# 1. Tìm những đơn hàng chưa được thanh toán
def getUnpaidOrders():
    orders = r.keys("Order:*")
    for order in orders:
        is_paid = int(r.hget(order, "is_paid"))

        if is_paid == 0:
            order_id = order.decode().split(":")[1]  # Order:1 => 1
            print("Mã đơn hàng: {}".format(order_id))

            # In thông tin sản phẩm trong giỏ hàng
            printCartDetail(order_id)


# 2. Tìm những đơn hàng có số lượng sản phẩm lớn hơn 5
def getOrdersWithMoreThan5Products():
    orders = r.keys("Order:*")
    for order in orders:
        order_id = order.decode().split(":")[1]  # Order:1 => 1
        order_details = r.zrange("Cart:" + order_id, 0, -1, withscores=True)
        total = 0
        for product in order_details:
            total += product[1]
        if total > 5:
            print("Mã đơn hàng: {}".format(order_id))

            # In thông tin sản phẩm trong giỏ hàng
            printCartDetail(order_id)


# 3. Tính tổng giá tiền cho một đơn hàng
def getTotalPrice(order_id):
    order_details = r.zrange("Cart:" + order_id, 0, -1, withscores=True)
    total = 0
    for product in order_details:
        product_price = int(r.hget("Product:" + product[0].decode(), "price"))
        total += product_price * product[1]
    return total


# 4. Liệt kê tất cả các đơn hàng của một người dùng
def getAllOrdersOfUser(user_id):
    orders = r.keys("Order:*")
    for order in orders:
        order_id = order.decode().split(":")[1]  # Order:1 => 1
        order_user_id = r.hget("Order:" + order_id, "user_id").decode()
        if order_user_id == user_id:
            print("Mã đơn hàng: {}".format(order_id))

            # In thông tin sản phẩm trong giỏ hàng
            printCartDetail(order_id)


# 5. Cho biết sản phẩm X xuất hiện trên bao nhiêu đơn hàng
def getProductCountInOrders(product_id):
    orders = r.keys("Order:*")
    count = 0
    for order in orders:
        order_id = order.decode().split(":")[1]
        if r.zscore("Cart:" + order_id, product_id) is not None:
            count += 1
    print("Sản phẩm {} xuất hiện trên {} đơn hàng".format(product_id, count))


# 6. Xóa sản phẩm X trong đơn hàng Y
def deleteProductInOrder(product_id, order_id):
    # check if product exists in order
    if r.zscore("Cart:" + order_id, product_id) is not None:
        r.zrem("Cart:" + order_id, product_id)
        print("Đã xóa sản phẩm {} trong đơn hàng {}".format(product_id, order_id))
    else:
        print("Không tìm thấy sản phẩm {} trong đơn hàng {}".format(product_id, order_id))


# 7. Tăng số lượng sản phẩm X trong đơn hàng Y lên 1 đơn vị
def increaseProductQuantityInOrder(product_id, order_id):
    # check if product exists in order
    if r.zscore("Cart:" + order_id, product_id) is not None:
        r.zincrby("Cart:" + order_id, 1, product_id)
        print("Đã tăng số lượng sản phẩm {} trong đơn hàng {} lên 1 đơn vị".format(product_id, order_id))
    else:
        print("Không tìm thấy sản phẩm {} trong đơn hàng {}".format(product_id, order_id))


# 8. Xóa tất cả sản phẩm trong đơn hàng
def deleteAllProductsInOrder(order_id):
    if r.delete("Cart:" + order_id) == 1:
        print("Đã xóa tất cả sản phẩm trong đơn hàng {}".format(order_id))
    else:
        print("Không tìm thấy đơn hàng {}".format(order_id))


# 9. Tìm đơn hàng có tổng giá trị lớn nhất
def getLargestOrder():
    orders = r.keys("Order:*")
    largest_order = None
    largest_order_price = 0
    for order in orders:
        order_id = order.decode().split(":")[1]  # Order:1 => 1
        order_price = getTotalPrice(order_id)
        if order_price > largest_order_price:
            largest_order = order_id
            largest_order_price = order_price
    print("Đơn hàng có tổng giá trị lớn nhất là đơn hàng {} với tổng tiền = {}".format(largest_order, largest_order_price))


# 10 Tìm sản phẩm xuất hiện nhiều đơn hàng nhất
def getMostPopularProduct():
    products = r.keys("Product:*")
    most_popular_product = None
    most_popular_product_count = 0
    for product in products:
        product_id = product.decode().split(":")[1]  # Product:1 => 1

        orders = r.keys("Order:*")
        product_count = 0
        for order in orders:
            order_id = order.decode().split(":")[1]
            if r.zscore("Cart:" + order_id, product_id) is not None:
                product_count += 1

        if product_count > most_popular_product_count:
            most_popular_product = product_id
            most_popular_product_count = product_count
    print("Sản phẩm xuất hiện nhiều đơn hàng nhất là sản phẩm {} với số lần xuất hiện = {}".format(most_popular_product,most_popular_product_count))


# Hiển thị các  mã sản phẩm và thông tin các sản phẩm
def printProducts():
    products = r.keys("Product:*")
    for product in products:
        product_id = product.decode().split(":")[1]  # Product:1 => 1
        product_name = r.hget(product, "name").decode()
        product_price = r.hget(product, "price").decode()
        print("Mã sản phẩm: {}".format(product_id))
        print("Tên sản phẩm: {}".format(product_name))
        print("Giá sản phẩm: {}".format(product_price))
        print("==========================================")


# Hiển thị các mã đơn hàng và thông tin các đơn hàng
def printOrders():
    orders = r.keys("Order:*")
    for order in orders:
        order_id = order.decode().split(":")[1]  # Order:1 => 1
        print("Mã đơn hàng: {}".format(order_id))


# Hiển thị các mã nguời dùng và thông tin các người dùng
def printUsers():
    users = r.keys("User:*")
    for user in users:
        user_id = user.decode().split(":")[1]  # User:1 => 1
        user_name = r.hget(user, "name").decode()
        print("Mã người dùng: {}".format(user_id))
        print("Tên người dùng: {}".format(user_name))
        print("==========================================")


if __name__ == "__main__":
    while True:
        print("1. Tìm những đơn hàng chưa được thanh toán")
        print("2. Tìm những đơn hàng có số lượng sản phẩm lớn hơn 5")
        print("3. Tính tổng giá tiền cho một đơn hàng")
        print("4. Liệt kê tất cả các đơn hàng của một người dùng")
        print("5. Cho biết sản phẩm X xuất hiện trên bao nhiêu đơn hàng")
        print("6. Xóa sản phẩm X trong đơn hàng Y")
        print("7. Tăng số lượng sản phẩm X trong đơn hàng Y lên 1 đơn vị")
        print("8. Xóa tất cả sản phẩm trong đơn hàng")
        print("9. Tìm đơn hàng có tổng giá trị lớn nhất")
        print("10. Tìm sản phẩm xuất hiện nhiều đơn hàng nhất")
        print("0. Thoát")
        choice = int(input("Nhập lựa chọn: "))
        print("")

        if choice == 1:
            print("Những đơn hàng chưa được thanh toán:")
            getUnpaidOrders()
        elif choice == 2:
            print("Những đơn hàng có số lượng sản phẩm lớn hơn 5:")
            getOrdersWithMoreThan5Products()
        elif choice == 3:
            printOrders()
            order_id = input("Nhập mã đơn hàng: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Tổng giá tiền cho đơn hàng {} là: {}".format(order_id, getTotalPrice(order_id)))
        elif choice == 4:
            printUsers()
            user_id = input("Nhập mã người dùng: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Tất cả các đơn hàng của người dùng {}:".format(user_id))
            getAllOrdersOfUser(user_id)
        elif choice == 5:
            printProducts()
            product_id = input("Nhập mã sản phẩm: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            getProductCountInOrders(product_id)
        elif choice == 6:
            printOrders()
            order_id = input("Nhập mã đơn hàng: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            printCartDetail(order_id)
            product_id = input("Nhập mã sản phẩm: ")
            deleteProductInOrder(product_id, order_id)
        elif choice == 7:
            printOrders()
            order_id = input("Nhập mã đơn hàng: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            printCartDetail(order_id)
            product_id = input("Nhập mã sản phẩm: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            increaseProductQuantityInOrder(product_id, order_id)
        elif choice == 8:
            printOrders()
            order_id = input("Nhập mã đơn hàng: ")
            os.system('cls' if os.name == 'nt' else 'clear')
            deleteAllProductsInOrder(order_id)
        elif choice == 9:
            getLargestOrder()
        elif choice == 10:
            getMostPopularProduct()
        elif choice == 0:
            exit()
        else:
            print("Lựa chọn không hợp lệ!")

        input("Nhấn Enter để tiếp tục...")
        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
