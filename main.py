from sql import SqlWrapper
from tabulate import tabulate

from typing import Tuple, Union, List

"""
Store database in the root directory as 'database'  or specify when calling SqlWrapper
"""


class ParanaShopperSession:
    def __init__(self) -> None:
        self.sql = SqlWrapper()
        self.shopper_id = self.get_shopper_id()
        
        self.welcome()
        
        self.basket = self.get_basket_id()
        
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
        If there is basket created from today, use that basket and return the basket_id
        """
        return self.sql.select_query("SELECT basket_id "
                                 "FROM shopper_baskets "
                                 "WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now') "
                                 "ORDER BY basket_created_date_time DESC "
                                 "LIMIT 1", sql_parameters=(self.shopper_id,))
    
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
        print(tabulate(results, headers), "\n")
        
    def display_order_history(self):
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
            
        self.main_loop()
        
    
    def main_menu(self) -> int:
        """
        Displays the main menu, returning the navigation integer
        """
        print("PARANÁ – SHOPPER MAIN MENU\n"
              "----------------------------------------------------\n"
              "1.	Display your order history\n"
              "2.	Add an item to your basket\n"
              "3.	View your basket\n"
              "4.	Change the quantity of an item in your basket\n"
              "5.	Remove an item from your basket\n"
              "6.	Checkout\n"
              "7.	Exit\n")
        return int(input())
    
    def main_loop(self) -> None:
        """
        The main loop of the session
        """
        # NOTE: match/case statements are python 3.10+
        match self.main_menu():
            
            case 1:
                self.display_order_history()
            
            case 2:
                raise NotImplementedError("Add an item to your basket")
            
            case 3:
                raise NotImplementedError("View your basket")
            
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