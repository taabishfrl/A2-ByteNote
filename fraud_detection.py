from processing_line import Transaction
from data_structures import ArrayR
from data_structures import HashTableSeparateChaining
from algorithms import insertion_sort


class FraudDetection:
    def __init__(self, transactions):
        self.transactions = transactions

    def detect_by_blocks(self):
        """
        Analyse your time complexity of this method.
        """
        if len(self.transactions) == 0:
            return (1, 1)
        
        sig_length = len(self.transactions[0].signature)
        
        max_suspicion = 1
        best_block_size = 1
        
        for block_size in range(1, sig_length + 1):
            suspicion_score = self.calculate_suspicion(block_size)
            
            if suspicion_score > max_suspicion:
                max_suspicion = suspicion_score
                best_block_size = block_size
        
        return (best_block_size, max_suspicion)

    def calculate_suspicion(self, block_size):
        """
        """
        groups = HashTableSeparateChaining()
        
        for i in range(len(self.transactions)):
            transaction = self.transactions[i]
            signature = transaction.signature
            
            final_form = self.transform_signature(signature, block_size)
            
            try:
                count = groups[final_form]
                groups[final_form] = count + 1
            except KeyError:
                groups[final_form] = 1
        
        suspicion_score = 1
        for count in groups:
            suspicion_score *= count
        
        return suspicion_score
    
    def transform_signature(self, signature, block_size):
        """
        """
        num_complete_blocks = len(signature) // block_size
        blocks = ArrayR(num_complete_blocks)
        
        for i in range(num_complete_blocks):
            start_idx = i * block_size
            block = signature[start_idx:start_idx + block_size]
            blocks[i] = block
        
        if num_complete_blocks > 0:
            sorted_blocks = insertion_sort(blocks)
        else:
            sorted_blocks = blocks
        
        final_form = ""
        for i in range(num_complete_blocks):
            final_form += sorted_blocks[i]
        
        remaining_start = num_complete_blocks * block_size
        if remaining_start < len(signature):
            final_form += signature[remaining_start:]
        
        return final_form

    def rectify(self, functions):
        pass

        
if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    def to_array(lst):
        """
        Helper function to create an ArrayR from a list.
        """
        lst = [to_array(item) if isinstance(item, list) else item for item in lst]
        return ArrayR.from_list(lst)

    # Here is something to get you started with testing detect_by_blocks
    print("<------- Testing detect_by_blocks! ------->")
    # Let's create 2 transactions and set their signatures
    tr1 = Transaction(1, "Alice", "Bob")
    tr2 = Transaction(2, "Alice", "Bob")

    # I will intentionally give the signatures that would put them in the same groups
    # if the block size was 1 or 2.
    tr1.signature = "aabbcc"
    tr2.signature = "ccbbaa"

    # Let's create an instance of FraudDetection with these transactions
    fd = FraudDetection([tr1, tr2])

    # Let's test the detect_by_blocks method
    block_size, suspicion_score = fd.detect_by_blocks()

    # We print the result, hopefully we should see either 1 or 2 for block size, and 2 for suspicion score.
    print(f"Block size: {block_size}, Suspicion score: {suspicion_score}")

    # I'm putting this line here so you can find where the testing ends in the terminal, but testing is by no means
    # complete. There are many more scenarios you'll need to test. Follow what we did above.
    print("<--- Testing detect_by_blocks finished! --->\n")

    # ----------------------------------------------------------

    # Here is something to get you started with testing rectify
    print("<------- Testing rectify! ------->")
    # I'm creating 4 simple transactions...
    transactions = [
        Transaction(1, "Alice", "Bob"),
        Transaction(2, "Alice", "Bob"),
        Transaction(3, "Alice", "Bob"),
        Transaction(4, "Alice", "Bob"),
    ]

    # Then I create two functions and to make testing easier, I use the timestamps I
    # gave to transactions to return the value I want for each transaction.
    def function1(transaction):
        return [2, 1, 1, 50][transaction.timestamp - 1]

    def function2(transaction):
        return [1, 2, 3, 4][transaction.timestamp - 1]

    # Now I create an instance of FraudDetection with these transactions
    fd = FraudDetection(to_array(transactions))

    # And I call rectify with the two functions
    result = fd.rectify(to_array([function1, function2]))

    # The expected result is (function2, 0) because function2 will give us a max probe chain of 0.
    # This is the same example given in the specs
    print(result)
    
    # I'll also use an assert statement to make sure the returned function is indeed the correct one.
    # This will be harder to verify by printing, but can be verified easily with an `assert`:
    assert result == (function2, 0), f"Expected (function2, 0), but got {result}"

    print("<--- Testing rectify finished! --->")