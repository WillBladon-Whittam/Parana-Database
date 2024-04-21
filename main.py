from sql import SqlWrapper
from tabulate import tabulate
import datetime

from typing import Tuple, Union, List

"""
Store database in the root directory as 'database' or specify when calling SqlWrapper

Links Used:
https://learnpython.com/blog/print-table-in-python/
https://learnsql.com/cookbook/how-to-number-rows-in-sql/

"""


class ParanaShopperSession:
    def __init__(self) -> None:
        self.sql = SqlWrapper()
        self.shopper_id = self.get_shopper_id()
        
        self.welcome()
        
        self.basket_id = self.get_basket_id()
        if not self.basket_id:
            self.basket_id = self.create_basket()
        self.basket_id = self.basket_id[0]
        self.main_loop()

    def get_shopper_id(self) -> int:
        """
        Return the shopper ID, validating that the shopper ID is in the database
        """
        shopper_id = int(input("Please enter your Shopper ID: "))
        shoppers = self.sql.select_query("SELECT shopper_id "
                                         "FROM shoppers")
        if shopper_id not in [shopper[0] for shopper in shoppers]:
            raise ValueError(f"Shopper ID {shopper_id} is not a valid Shopper ID")
        return shopper_id
    
    def get_basket_id(self) -> int:
        """
        If there is a basket created from today, use that basket and return the basket_id
        """
        return self.sql.select_query("SELECT basket_id "
                                     "FROM shopper_baskets "
                                     "WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now') "
                                     "ORDER BY basket_created_date_time DESC "
                                     "LIMIT 1", sql_parameters=(self.shopper_id,), fetch_all=False)
        
    def create_basket(self) -> int:
        """
        If a basket is not already created from today, then create a new basket
        """
        self.sql.insert_query("INSERT INTO shopper_baskets (shopper_id, basket_created_date_time) "
                              "VALUES (?, ?)", sql_parameters=(self.shopper_id, datetime.datetime.now().strftime("%Y-%m-%d"),))
        return self.sql.cursor.lastrowid
    
    def welcome(self) -> None:
        """
        Prints a welcome message to the shopper
        """
        shopper_first_name, shopper_surname = self.sql.select_query("SELECT shopper_first_name, shopper_surname "
                                                                    "FROM shoppers "
                                                                    "WHERE shopper_id = ? ", 
                                                                    sql_parameters=(self.shopper_id,), 
                                                                    fetch_all=False)
        
        print(f"Welcome {shopper_first_name} {shopper_surname}!\n")
        
    def pretty_print(self, results: Union[List[Tuple], Tuple], headers: List[str] = []) -> None:
        """
        Pretty print a table
        
        Args:
            results: Results returned from an SQL query
            headers: The headers for the table
        """
        print(tabulate(results, headers), "\n")
        
    def display_order_history(self) -> None:
        """
        Display the order history of the shopper (Option 1)
        """
        order_history = self.sql.select_query("SELECT so.order_id, "
                                              "STRFTIME('%d-%m-%Y', so.order_date), "
                                              "p.product_description, "
                                              "se.seller_name, "
                                              "PRINTF('£%.2f',op.price), "
                                              "op.quantity, "
                                              "ordered_product_status "
                                              "FROM shoppers as s "
                                              "INNER JOIN shopper_orders so ON s.shopper_id = so.shopper_id "
                                              "INNER JOIN ordered_products op ON so.order_id = op.order_id "
                                              "INNER JOIN product_sellers ps ON op.product_id = ps.product_id "
                                              "AND op.seller_id = ps.seller_id "
                                              "INNER JOIN sellers se ON ps.seller_id = se.seller_id "
                                              "INNER JOIN products p ON ps.product_id = p.product_id "
                                              "WHERE s.shopper_id= ? "
                                              "ORDER BY so.order_date DESC", sql_parameters=(self.shopper_id,))
        if not order_history:
            print("No orders placed by this customer\n")
        else:
            self.pretty_print(results=order_history, headers=["Order ID", "Order Date", "Product Description", "Seller", "Price", "Qty", "Status"])
            
    def display_options(self, options: List[Tuple[str]]) -> None:
        """
        Displays the options returned from an SQL query as a numbered list
        """
        for i, option in enumerate(options, start=1):
            print(f"{i}.\t{"  ".join(str(row) for row in option)}")
        print("\n")
        
    def prompt_number(self, prompt: str, _range: Tuple[int, Union[int, None]] = None, error_message: str = "Invalid Value!") -> int:
        """
        Prompts the user for a number between a specific range.
        """
        selected_option = None
        if _range is None:  # If no range is specified
            selected_option = int(input(prompt))
            return selected_option
        elif _range[1] is None:  # If there is a minimum value
            while (selected_option or -1) < _range[0]:
                selected_option = int(input(prompt))
                if selected_option <= _range[0]:
                    print(f"{error_message}\n")
        else:  # If there is a range of 2 values
            while selected_option not in range(_range[0], _range[1]):
                selected_option = int(input(prompt))
                if selected_option not in range(_range[0], _range[1]):
                    print(f"{error_message}\n")
        return selected_option
 
    def add_item(self) -> None:
        """
        Add item to the shoppers basket.
        Choose product categories -> products -> sellers -> quantity
        """
        product_categories = self.sql.select_query("SELECT category_description "
                                                   "FROM categories "
                                                   "ORDER BY category_description ASC ")
        
        self.display_options(product_categories)
        selected_category = self.prompt_number(prompt="Enter the number against the product category you want to choose: ", 
                                               _range=(1, len(product_categories)+1))
                
        selected_category_id = self.sql.select_query("SELECT category_id "
                                                     "FROM categories "
                                                     "WHERE category_description = ?", sql_parameters=product_categories[selected_category-1], fetch_all=False)
        products = self.sql.select_query("SELECT product_description "
                                         "FROM products "
                                         "WHERE category_id = ? "
                                         "ORDER BY product_description ASC ", sql_parameters=selected_category_id)

        self.display_options(products)
        selected_product = self.prompt_number(prompt="Enter the number against the product you want to choose: ", 
                                              _range=(1, len(products)+1))
        
        selected_product_id = self.sql.select_query("SELECT product_id "
                                                    "FROM products "
                                                    "WHERE product_description = ?", sql_parameters=products[selected_product-1], fetch_all=False)
        
        sellers = self.sql.select_query("SELECT s.seller_name, PRINTF('(£%.2f)', ps.price) "
                                        "FROM sellers s "
                                        "INNER JOIN product_sellers ps ON s.seller_id = ps.seller_id "
                                        "WHERE ps.product_id = ? "
                                        "ORDER BY s.seller_name ASC ", sql_parameters=selected_product_id)        
        
        self.display_options(sellers)
        selected_seller = self.prompt_number(prompt="Enter the number against the seller you want to choose: ", 
                                             _range=(1, len(sellers)+1))
        
        selected_seller_id = self.sql.select_query("SELECT seller_id "
                                                   "FROM sellers "
                                                   "WHERE seller_name = ?", sql_parameters=sellers[selected_seller-1][0], fetch_all=False)
        
        quantity = self.prompt_number(prompt="Enter the quantity of the selected product you want to buy: ", _range=(1, None),
                                      error_message="The quantity must be greater than 0")
        

        self.sql.insert_query("INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price) "
                              "VALUES (?, ?, ?, ?, ?)", 
                              sql_parameters=(self.basket_id, selected_product_id[0], selected_seller_id[0], quantity, 
                                              self.remove_money_format(sellers[selected_seller-1][1])))  # Not a very elegant solution...
        
        print("Item added to your basket")
        
    @staticmethod
    def remove_money_format(value: str) -> str:
        return value.replace("£","").replace(")", "").replace("(", "")
        
    def display_basket(self) -> None:
        basket_contents = self.sql.select_query("SELECT ROW_NUMBER() OVER(), p.product_description, s.seller_name, bc.quantity, PRINTF('£%.2f', bc.price), PRINTF('£%.2f', bc.price * bc.quantity) "
                                                "FROM basket_contents bc "
                                                "INNER JOIN product_sellers ps ON bc.product_id = ps.product_id and bc.seller_id = ps.seller_id "
                                                "INNER JOIN products p ON p.product_id = ps.product_id "
                                                "INNER JOIN sellers s ON s.seller_id = ps.seller_id "
                                                "WHERE bc.basket_id = ?", sql_parameters=self.basket_id)    
        
        if not basket_contents:
            print("Your basket is empty\n")
            
        else:
            # Abit of a botched way...
            basket_contents.append((None, None, None, None, "Basket Total", f'£{sum([float(self.remove_money_format(item[4])) for item in basket_contents])}'))
            self.pretty_print(basket_contents, headers=["Basket Item", "Product Description", "Seller Name", "Qty", "Price", "Total"])

    
    def main_menu(self) -> int:
        """
        Displays the main menu, returning the navigation integer
        """
        print("PARANÁ – SHOPPER MAIN MENU\n"
              "----------------------------------------------------\n"
              "1.\tDisplay your order history\n"
              "2.\tAdd an item to your basket\n"
              "3.\tView your basket\n"
              "4.\tChange the quantity of an item in your basket\n"
              "5.\tRemove an item from your basket\n"
              "6.\tCheckout\n"
              "7.\tExit\n")
        return int(input("Select an option: "))
    
    def main_loop(self) -> None:
        """
        The main loop of the session
        """
        while True:
            # NOTE: match/case statements are python 3.10+
            match self.main_menu():
                
                case 1:
                    self.display_order_history()
                
                case 2:
                   self.add_item()
                
                case 3:
                    self.display_basket()
                
                case 4:
                    raise NotImplementedError("Change the quantity of an item in your basket")
                
                case 5:
                    raise NotImplementedError("Remove an item from your basket")
                
                case 6:
                    raise NotImplementedError("Checkout")
                
                case 7:
                    self.sql.close()
                    quit()
                    
                case _:
                    print("Invalid Value")  # Close program?
                

if __name__ == "__main__":
    # Valid Shopper 10023, 10000
    ParanaShopperSession()