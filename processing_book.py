from data_structures import ArrayR
from processing_line import Transaction


class ProcessingBook:

    LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, level=0):
        self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
        self.level = level  
        self.error_count = 0
        self.transaction_count = 0
    
    def page_index(self, character):
        """
        You may find this method helpful. It takes a character and returns the index of the relevant page.
        Time complexity of this method is O(1), because it always only checks 36 characters.
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)
    
    def __setitem__(self, transaction, amount):
        """
        :complexity: Best case is O(1), where n is len(transaction_signature), Best case happens when the page is empty, thereby
        no collisions will occur. In this case, there is no recursive call to create a new nested book. The length of the signature
        is also a constant of 36, therefore it runs in O(1) time. The other operations also run in O(1) time.

        Worst case is also O(n), where n is len(transaction_signature), Worst case happens when the page is not empty, and
        the method has to created multiple nested books to handle collisions. In this case, there is multiple recursive calls
        and the method has to run in O(n) time.

        """
        
        char = transaction.signature[self.level]
        page_idx = self.page_index(char)
        
        current_page = self.pages[page_idx]
        
        if current_page is None:
            self.pages[page_idx] = (transaction, amount)
            self.transaction_count += 1
            
        elif isinstance(current_page, tuple):
            stored_transaction, stored_amount = current_page
            
            if stored_transaction.signature == transaction.signature:
                if stored_amount == amount:
                    return
                else:
                    self.error_count += 1
                    return
            else:
                nested_book = ProcessingBook(level=self.level + 1)
                
                nested_book[stored_transaction] = stored_amount
                
                nested_book[transaction] = amount
                
                self.pages[page_idx] = nested_book

                self.transaction_count += 1
                
        elif isinstance(current_page, ProcessingBook):
            old_error_count = current_page.error_count
            old_count = current_page.transaction_count

            current_page[transaction] = amount
            
            self.error_count += current_page.error_count - old_error_count
            self.transaction_count += current_page.transaction_count - old_count

    def __getitem__(self, transaction):
        """
        :complexity: Best case is O(1), where n is the len(transaction.signature). Best case happens when the transaction is 
        found at the top level, and therefore the function does not have to perform any recursive calls, 
        all other operations in the method run in O(1) time.

        Worst case is O(n), where n is the len(transaction.signature), Worst case happens when the transaction is at the very end,
        and therefore the function has to perform multiple recursive calls to retrieve the item, this runs in O(n) time. 
        """
        if self.level >= len(transaction.signature):
            raise KeyError("Transaction not found")
        
        char = transaction.signature[self.level]
        page_idx = self.page_index(char)
        
        current_page = self.pages[page_idx]
        
        if current_page is None:
            raise KeyError("Transaction not found")
            
        elif isinstance(current_page, tuple):
            stored_transaction, stored_amount = current_page
            
            if stored_transaction.signature == transaction.signature:
                return stored_amount
            else:
                raise KeyError("Transaction not found")
                
        elif isinstance(current_page, ProcessingBook):
            return current_page[transaction]
        
        raise KeyError("Transaction not found")
    
    def __delitem__(self, transaction):
        """
        :complexity: Best case is O(1), where n is len(transaction.signature), Best case happens when the transaction to be deleted
        is at the very top level, and therefore the function does not have to perform any recursive calls, the rest of the operations
        run in O(1) time.

        Worst case is O(n), where n is len(transaction.signature), Worst case happens when the transaction to be deleted is deep in the nested books or
        at the very end. Therefore, the function has to perform multiple recursive calls to retrieve and delete the item. This runs in
        O(n) time.
        """
        if self.level >= len(transaction.signature):
            raise KeyError("Transaction not found")
        
        char = transaction.signature[self.level]
        page_idx = self.page_index(char)
        
        current_page = self.pages[page_idx]
        
        if current_page is None:
            raise KeyError("Transaction not found")
            
        elif isinstance(current_page, tuple):
            stored_transaction, stored_amount = current_page
            
            if stored_transaction.signature == transaction.signature:
                self.pages[page_idx] = None
                self.transaction_count -= 1
            else:
                raise KeyError("Transaction not found")
                
        elif isinstance(current_page, ProcessingBook):

            old_count = current_page.transaction_count
            current_page.__delitem__(transaction)

            self.transaction_count -= (old_count - current_page.transaction_count)
            
            if current_page.transaction_count == 1:
                for i in range(len(current_page.pages)):
                    if current_page.pages[i] is not None:
                        if isinstance(current_page.pages[i], tuple):
                            self.pages[page_idx] = current_page.pages[i]
                            break
            elif current_page.transaction_count == 0:
                self.pages[page_idx] = None
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.
        """
        return self.error_count
    
    def __len__(self):
        return self.transaction_count
    
    def __iter__(self):
        """
        :complexity: Best and Worst case is O(1), as it simply returns the Iterator Class.
        """
        return ProcessingBookIterator(self)

class ProcessingBookIterator:

    
    def __init__(self, processing_book):
        """
        :complexity: Best and Worst case is O(1), All operations in this method run in O(1) time as they are assignments.
        """
        self.processing_book = processing_book
        self.current_page = 0
        self.nested_iterator = None
    
    def __iter__(self):
        """
        :complexity: Best and Worst case is O(1), The iterator is simply returning itself for ProcessingBook.
        """
        return self
    
    def __next__(self):
        """
        :complexity: Best case is O(1), this is the case when the page contains a direct transaction with no nested books, for example
        "a...", "b...". Therefore, the method does not have to perform any recursive calls to access the nested books, The rest of the operations
        in the method run in O(1) time.

        Worst case is O(n), where n is len(self.processing_book.pages), Worst case happens when the prefix of the transactions are similar,
        for example "aaaaaab","aaaaaaac", therefore the method has to perform multiple recursive calls to access the nested books, this runs
        in O(n) time.
        """
        if self.nested_iterator is not None:
            try:
                return next(self.nested_iterator)
            except StopIteration:
                self.nested_iterator = None
        
        while self.current_page < len(self.processing_book.pages):
            page = self.processing_book.pages[self.current_page]
            
            if page is not None:
                if isinstance(page, tuple):
                    transaction, amount = page
                    self.current_page += 1
                    return (transaction, amount)
                    
                elif isinstance(page, ProcessingBook):
                    self.nested_iterator = iter(page)
                    self.current_page += 1
                    try:
                        return next(self.nested_iterator)
                    except StopIteration:
                        self.nested_iterator = None
                        continue
            
            self.current_page += 1
        
        raise StopIteration
    
    def sample(self, required_size):
        """
        1054 Only - 1008/2085 welcome to attempt if you're up for a challenge, but no marks are allocated.
        Analyse your time complexity of this method.
        """
        pass

if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.

    # Let's create a few transactions
    tr1 = Transaction(123, "sender", "receiver")
    tr1.signature = "abc123"

    tr2 = Transaction(124, "sender", "receiver")
    tr2.signature = "0bbzzz"

    tr3 = Transaction(125, "sender", "receiver")
    tr3.signature = "abcxyz"

    # Let's create a new book to store these transactions
    book = ProcessingBook()

    book[tr1] = 10
    print(book[tr1])  # Prints 10

    book[tr2] = 20
    print(book[tr2])  # Prints 20

    book[tr3] = 30    # Ends up creating 3 other nested books
    print(book[tr3])  # Prints 30
    print(book[tr2])  # Prints 20

    book[tr2] = 40
    print(book[tr2])  # Prints 20 (because it shouldn't update the amount)

    del book[tr1]     # Delete the first transaction. This also means the nested books will be collapsed. We'll test that in a bit.
    try:
        print(book[tr1])  # Raises KeyError
    except KeyError as e:
        print("Raised KeyError as expected:", e)

    print(book[tr2])  # Prints 20
    print(book[tr3])  # Prints 30

    # We deleted T1 a few lines above, which collapsed the nested books.
    # Let's make sure that actually happened. We should be able to find tr3 sitting
    # in Page A of the book:
    print(book.pages[book.page_index('a')])  # This should print whatever details we stored of T3 and only T3
