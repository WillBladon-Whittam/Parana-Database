from sql import SqlWrapper
from tabulate import tabulate
import datetime

from typing import Tuple, Union, List

"""
Store database in the root directory as 'database' or specify when calling SqlWrapper

Links Used:
https://learnpython.com/blog/print-table-in-python/ -> Pretty print a SQL query results in a table
https://learnsql.com/cookbook/how-to-number-rows-in-sql/ -> Number rows returned from an SQL Query
https://www.sqlite.org/lang_datefunc.html -> DATE('now'), was returung the incorrect date at midnight. Needs to use local timezone.
"""


class ParanaShopperSession:
    """
    Creates a Shopper session based on the Parana database
    """

    def __init__(self) -> None:
        self.sql = SqlWrapper()
        self.shopper_id = self.get_shopper_id()

        self.welcome()

        self.basket_id = self.get_basket_id()
        if not self.basket_id:
            self.basket_id = self.create_basket()
        else:
            self.basket_id = self.basket_id[0]
        self.main_loop()
        
    @staticmethod
    def pretty_print(results: Union[List[Tuple], Tuple], headers: List[str] = []) -> None:
        """
        Pretty print a table based on the results from an SQL table
        """
        print(tabulate(results, headers), "\n")
        
    @staticmethod
    def display_options(options: List[Tuple[str]]) -> None:
        """
        Displays the options returned from an SQL query as a numbered list
        """
        for i, option in enumerate(options, start=1):
            print(f"{i}.\t{"  ".join(str(row) for row in option)}")
        print("\n")

    @staticmethod
    def prompt_yes_no(prompt: str) -> bool:
        """
        Prompts the user for a Y/N response
        """
        selected_option = None
        while selected_option not in ["Y", "N", "y", "n"]:
            selected_option = input(prompt)
            if selected_option not in ["Y", "N", "y", "n"]:
                print("Please enter Y/N\n")
        if selected_option.upper() == "Y":
            return True
        elif selected_option.upper() == "N":
            return False

    @staticmethod
    def prompt_number(prompt: str, _range: Tuple[int, Union[int, None]] = None, error_message: str = "Invalid Value!") -> int:
        """
        Prompts the user for a number between a specific range.
        """
        selected_option = -1
        if _range is None:  # If no range is specified
            while not selected_option > 0:
                try:
                    selected_option = int(input(prompt))
                except ValueError:
                    print(f"{error_message}\n")
                    continue
                if selected_option <= 0:
                    print(f"{error_message}\n")
            return selected_option
        elif _range[1] is None:  # If there is a minimum value
            while not _range[0] <= selected_option:
                try:
                    selected_option = int(input(prompt))
                except ValueError:
                    print(f"{error_message}\n")
                    continue
                if selected_option <= _range[0]:
                    print(f"{error_message}\n")
        else:  # If there is a range of 2 values
            while selected_option not in range(_range[0], _range[1]+1):
                try:
                    selected_option = int(input(prompt))
                except ValueError:
                    print(f"{error_message}\n")
                    continue
                if selected_option not in range(_range[0], _range[1]+1):
                    print(f"{error_message}\n")
        return selected_option
    
    @staticmethod
    def remove_money_format(value: str) -> List[Tuple[int, str]]:
        """
        Remove strings that are formatted with £ and/or ().
        e.g. convert (£5.32) -> 5.32
        """
        return value.replace("£", "").replace(")", "").replace("(", "")

    def get_shopper_id(self) -> int:
        """
        Return the shopper ID, validating that the shopper ID is in the database
        """
        shopper_id = int(input("Please enter your Shopper ID: "))
        shoppers = self.sql.select_query("SELECT shopper_id "
                                         "FROM shoppers")
        if shopper_id not in [shopper[0] for shopper in shoppers]:
            print(f"Shopper ID {shopper_id} is not a valid Shopper ID")
            quit()
        return shopper_id

    def get_basket_id(self) -> int:
        """
        If there is a basket created from today, use that basket and return the basket_id
        """
        # Must use localtime, otherwise breaks at midnight
        return self.sql.select_query("SELECT basket_id "
                                     "FROM shopper_baskets "
                                     "WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now', 'localtime') "
                                     "ORDER BY basket_created_date_time DESC "
                                     "LIMIT 1", sql_parameters=(self.shopper_id,), fetch="one")

    def create_basket(self) -> int:
        """
        If a basket is not already created from today, then create a new basket
        """
        self.sql.update_table("INSERT INTO shopper_baskets (shopper_id, basket_created_date_time) "
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
                                                                    fetch="one")

        print(f"Welcome {shopper_first_name} {shopper_surname}!\n")

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
            self.pretty_print(results=order_history, headers=[
                              "Order ID", "Order Date", "Product Description", "Seller", "Price", "Qty", "Status"])

    def add_item(self) -> None:
        """
        Add item to the shoppers basket. (Option 2)
        Choose product categories -> products -> sellers -> quantity
        """
        product_categories = self.sql.select_query("SELECT category_description "
                                                   "FROM categories "
                                                   "ORDER BY category_description ASC ")
        self.display_options(product_categories)
        
        selected_category = self.prompt_number(prompt="Enter the number against the product category you want to choose: ",
                                               _range=(1, len(product_categories)))

        selected_category_id = self.sql.select_query("SELECT category_id "
                                                     "FROM categories "
                                                     "WHERE category_description = ?", sql_parameters=product_categories[selected_category-1], fetch="one")
        
        products = self.sql.select_query("SELECT product_description "
                                         "FROM products "
                                         "WHERE category_id = ? "
                                         "ORDER BY product_description ASC ", sql_parameters=selected_category_id)
        self.display_options(products)
        
        selected_product = self.prompt_number(prompt="Enter the number against the product you want to choose: ",
                                              _range=(1, len(products)))

        selected_product_id = self.sql.select_query("SELECT product_id "
                                                    "FROM products "
                                                    "WHERE product_description = ?", sql_parameters=products[selected_product-1], fetch="one")

        sellers = self.sql.select_query("SELECT s.seller_name, PRINTF('(£%.2f)', ps.price) "
                                        "FROM sellers s "
                                        "INNER JOIN product_sellers ps ON s.seller_id = ps.seller_id "
                                        "WHERE ps.product_id = ? "
                                        "ORDER BY s.seller_name ASC ", sql_parameters=selected_product_id)
        self.display_options(sellers)
        
        selected_seller = self.prompt_number(prompt="Enter the number against the seller you want to choose: ",
                                             _range=(1, len(sellers)))

        selected_seller_id = self.sql.select_query("SELECT seller_id "
                                                   "FROM sellers "
                                                   "WHERE seller_name = ?", sql_parameters=sellers[selected_seller-1][0], fetch="one")

        quantity = self.prompt_number(prompt="Enter the quantity of the selected product you want to buy: ", _range=(1, None),
                                      error_message="The quantity must be greater than 0")
        
        # NOTE: ix. in the brief says to create a new basket here, if there is not already one. This is done when initialising the session.

        query_status = self.sql.update_table("INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price) "
                                             "VALUES (?, ?, ?, ?, ?)",
                                             sql_parameters=(self.basket_id, selected_product_id[0], selected_seller_id[0], quantity,
                                                             self.remove_money_format(sellers[selected_seller-1][1]))) 

        if query_status is None:
            print("Item added to your basket\n")
        else:
            print("That item is already in your basket. Please edit the quantity of the item in Option 4, or delete the item in Option 5\n")

    def display_basket(self) -> None:
        """
        Display the contents of the shoppers basket (Option 3)
        """
        basket_contents = self.sql.select_query("SELECT ROW_NUMBER() OVER(), p.product_description, s.seller_name, bc.quantity, PRINTF('£%.2f', bc.price), PRINTF('£%.2f', bc.price * bc.quantity) "
                                                "FROM basket_contents bc "
                                                "INNER JOIN product_sellers ps ON bc.product_id = ps.product_id and bc.seller_id = ps.seller_id "
                                                "INNER JOIN products p ON p.product_id = ps.product_id "
                                                "INNER JOIN sellers s ON s.seller_id = ps.seller_id "
                                                "WHERE bc.basket_id = ?", sql_parameters=self.basket_id)

        if not basket_contents:
            print("Your basket is empty\n")
            return basket_contents
        else:
            # Abit of a botched way... looks okay so oh well.
            basket_contents.append((None, None, None, None, "Basket Total", f'£{sum(
                [float(self.remove_money_format(item[5])) for item in basket_contents])}'))
            self.pretty_print(basket_contents, headers=[
                              "Basket Item", "Product Description", "Seller Name", "Qty", "Price", "Total"])

        return basket_contents

    def change_quantity(self) -> None:
        """
        Change the quantity of an item in the basket. (Option 4)
        The basket_contents table has 2 primary keys. basket_id and product_id.
        So there can only be 1 of a product added to a basket, even if they are from different sellers.
        """
        basket_contents = self.display_basket()
        if not basket_contents:
            return

        # basket_contents is returned with the botched basket total column, so 2 instead of 1.
        if len(basket_contents) > 2:
            basket_item_number = self.prompt_number("Enter the basket item no. of the item you want to change: ", _range=(1, len(basket_contents)-1),
                                                    error_message="The basket item no. you have entered is invalid")
        else:
            basket_item_number = 1

        quantity = self.prompt_number("Enter the new quantity of the selected product you want to buy: ", _range=(1, None),
                                      error_message="The quantity must be greater than 0")

        self.sql.update_table("UPDATE basket_contents "
                              "SET quantity = ? "
                              "WHERE product_id = (SELECT product_id "
                              "FROM products "
                              "WHERE product_description = ?) and basket_id = ? ", sql_parameters=(quantity, basket_contents[basket_item_number-1][1], self.basket_id))

        self.display_basket()

    def remove_item(self) -> None:
        """
        Remove an item from the shoppers basket (Option 5)
        """
        basket_contents = self.display_basket()
        if not basket_contents:
            return

        # basket_contents is returned with the botched basket total column, so 2 instead of 1.
        if len(basket_contents) > 2:
            basket_item_number = self.prompt_number("Enter the basket item no. of the item you want to change: ", _range=(1, len(basket_contents)-1),
                                                    error_message="The basket item no. you have entered is invalid")
        else:
            basket_item_number = 1

        answer = self.prompt_yes_no(
            "Do you definitly want to delete this product from your basket (Y/N)? ")

        if answer:
            self.sql.update_table("DELETE FROM basket_contents "
                                  "WHERE product_id = (SELECT product_id "
                                  "FROM products WHERE "
                                  "product_description = ?) and basket_id = ?", sql_parameters=(basket_contents[basket_item_number-1][1], self.basket_id))

            self.display_basket()
        else:
            return

    def checkout(self) -> None:
        """
        Checkout the the shoppers basket. (Option 6)
        Add order to shoppers_orders and ordered_products tables.
        Remove the basket contents for the shopper and the basket from basket_contents and shopper_baskets
        """
        basket_contents = self.display_basket()
        if not basket_contents:
            return

        answer = self.prompt_yes_no(
            "Do you wish to proceed with the checkout (Y/N)? ")

        if answer:
            # Insert row into shoppers_orders
            self.sql.update_table("INSERT INTO shopper_orders (shopper_id, order_date, order_status) "
                                  "VALUES (?, ?, ?)", sql_parameters=(self.shopper_id, datetime.datetime.now().strftime("%Y-%m-%d"), "Placed"))
            order_id = self.sql.cursor.lastrowid
            
            # Insert row into ordered_products
            for item in basket_contents[:-1]:
                self.sql.update_table("INSERT INTO ordered_products (order_id, product_id, seller_id, quantity, price, ordered_product_status) "
                                      "VALUES (?, (SELECT product_id "
                                      "FROM products WHERE "
                                      "product_description = ?), (SELECT seller_id "
                                      "FROM sellers WHERE "
                                      "seller_name = ?), ?, ?, ?)", 
                                      sql_parameters=(order_id, item[1], item[2], item[3], self.remove_money_format(item[4]), "Placed"))

            # Delete rows in basket_contents associated with the basket
            self.sql.update_table("DELETE FROM basket_contents "
                                  "WHERE basket_id = ?", sql_parameters=(self.basket_id))

            # Delete basket in shopper_baskets
            self.sql.update_table("DELETE FROM shopper_baskets "
                                  "WHERE basket_id = ?", sql_parameters=(self.basket_id))

            print("Checkout complete, your order has been placed\n")

        else:

            return

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
        return self.prompt_number("Select an option: ", _range=(1, 7))

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
                    self.change_quantity()

                case 5:
                    self.remove_item()

                case 6:
                    self.checkout()

                case 7:
                    self.sql.close()
                    quit()


if __name__ == "__main__":
    ParanaShopperSession()
