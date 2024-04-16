from sql import SqlWrapper

"""
Store database in the root directory as 'database'  or specify when calling SqlWrapper
"""


class ParanaShopperSession:
    def __init__(self) -> None:
        self.sql = SqlWrapper()
        self.shopper_id = self.get_shopper_id()
        
        self.welcome()
        
        self.main_loop()

    def get_shopper_id(self) -> int:
        """
        Return the shopper ID, validating that the shopper ID is in the database
        """
        shopper_id = int(input("Please enter your Shopper ID: "))
        shoppers = self.sql.select_query(columns=["shopper_id"], table="shoppers")
        if shopper_id not in [shopper[0] for shopper in shoppers]:
            raise ValueError(f"Shopper ID {shopper_id} is not a valid Shopper ID")
        return shopper_id
    
    def welcome(self) -> None:
        """
        Prints a welcome message to the shopper
        """
        shopper_first_name, shopper_surname = self.sql.select_query(
            columns=["shopper_first_name", "shopper_surname"], table="shoppers", where=f"shopper_id == {self.shopper_id}", fetch_all=False)
        print(f"Welcome {shopper_first_name} {shopper_surname}!\n")
    
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
                raise NotImplementedError("Display your order history")
            
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
    # Valid Shopper 10023
    ParanaShopperSession()