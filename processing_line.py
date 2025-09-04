from data_structures.linked_stack import LinkedStack

class Transaction:
    def __init__(self, timestamp, from_user, to_user):
        self.timestamp = timestamp
        self.from_user = from_user
        self.to_user = to_user
        self.signature = None
    
    def sign(self):
        """
        :complexity: Best case is O(n), where n = len(str(timestamp)) + len(from_user) + len(to_user), The function has to
        concantenate the string and iterate through the string of n characters to assign an ascii_value which both run in O(n) time.
        In addition, the for loop that generates the signature runs in O(1) time.Regardless of the len(transaction_data), 
        there is no early-termination path since every character has to be processed.
        
        Worst case is also O(n), where n = len(str(timestamp)) + len(from_user) + len(to_user), this is the case as the 
        per-character loop dominates the runtime, the other operations are constant and therefore run in O(1) time.

        """

        transaction_data = str(self.timestamp) + self.from_user + self.to_user
        
        
        hash_value = 0
        prime_multiplier = 31  

        for char in transaction_data:
            if 'a' <= char <= 'z':
                ascii_value = ord(char) - ord('a')
            elif '0' <= char <= '9':
                ascii_value = ord(char) - ord('0') + 26
            else:
                ascii_value = ord(char) % 36
            
            hash_value = hash_value * prime_multiplier + ascii_value
        
        
        mod_value = 36 ** 36
        hash_value = hash_value % mod_value
        
        signature = ""
        LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        temp = hash_value
        for _ in range(36):
            signature = LEGAL_CHARACTERS[temp % 36] + signature
            temp = temp // 36
        
        self.signature = signature


class ProcessingLine:
    def __init__(self, critical_transaction):
        """
        :complexity: Best case is O(1), where the input size is critical_transaction, This happens when there are
        minimal initializations to be made. This function creates two LinkedStacks instances which takes O(1) time,
        and the rest of the operations run in O(1) time.

        Worst case is also O(1), where the input size is critical_transaction, this is the case as regardless of
        the number of initializations and assignments, the function performs a fixed number of operations and
        will always run in O(1) time.
        """
        self.critical_transaction = critical_transaction
        self.critical_timestamp = critical_transaction.timestamp

        self.before_stack = LinkedStack()
        self.after_stack = LinkedStack()

        self.is_locked = False
        self.iterator_created = False


    def add_transaction(self, transaction):
        """
        :complexity: Best case is O(1), where n is the transaction object. This is the case when the transaction is
        locked and therefore raises a runtime error, all operations in this function take O(1) time.

        Worst case is also O(1), where n is a transaction object. This happens regardless as the method always executes
        the same sequence of one conditional check, one comparison operation, and one stack push. Even if there are millions
        of transactions as all operations run in O(1) time .
        """
        if self.is_locked:
            raise RuntimeError("Cannot add transactions - line is locked for processing")
        
        if transaction.timestamp <= self.critical_timestamp:
            self.before_stack.push(transaction)
        else:
            self.after_stack.push(transaction)
    
    def __iter__(self):
        if self.iterator_created:
            raise RuntimeError("Iterator already created - cannot process line multiple times")
        
        self.is_locked = True
        self.iterator_created = True
        
        return ProcessingLineIterator(self)
    
class ProcessingLineIterator:
    
    def __init__(self, processing_line):
        self.processing_line = processing_line
        self.phase = "before"  
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.phase == "before":
            if not hasattr(self, 'before_temp_stack'):
                self.before_temp_stack = LinkedStack()
                
                while not self.processing_line.before_stack.is_empty():
                    self.before_temp_stack.push(self.processing_line.before_stack.pop())
            
            if not self.before_temp_stack.is_empty():
                transaction = self.before_temp_stack.pop()
                transaction.sign()  
                return transaction
            else:
                self.phase = "critical"
                return self.__next__()  
        
        elif self.phase == "critical":
            self.phase = "after"
            self.processing_line.critical_transaction.sign()  
            return self.processing_line.critical_transaction
        
        elif self.phase == "after":
            if not self.processing_line.after_stack.is_empty():
                transaction = self.processing_line.after_stack.pop()
                transaction.sign()  
                return transaction
            else:
                self.phase = "done"
                return self.__next__() 
        
        else: 
            raise StopIteration


if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    # Here's something to get you started...
    transaction1 = Transaction(50, "alice", "bob")
    transaction2 = Transaction(100, "bob", "dave")
    transaction3 = Transaction(120, "dave", "frank")

    line = ProcessingLine(transaction2)
    line.add_transaction(transaction3)
    line.add_transaction(transaction1)

    print("Let's print the transactions... Make sure the signatures aren't empty!")
    line_iterator = iter(line)
    while True:
        try:
            transaction = next(line_iterator)
            print(f"Processed transaction: {transaction.from_user} -> {transaction.to_user}, "
                  f"Time: {transaction.timestamp}\nSignature: {transaction.signature}")
        except StopIteration:
            break
