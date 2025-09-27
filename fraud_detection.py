from processing_line import Transaction
from data_structures import ArrayR
from data_structures import HashTableSeparateChaining
from algorithms import insertion_sort


class FraudDetection:
    def __init__(self, transactions):
        self.transactions = transactions

    def detect_by_blocks(self):
        """
        :complexity: Best case is O(N X L^2), where N is the number of transactions and L is the length of the signature, Best case
        happens when the block sizes are large, for example, S = 18, where S is the block size, therefore, 
        this would result in having to sort fewer blocks per signature, resulting in the sorting cost being O(1), 
        making the signature processing O(L) per transaction. Since we try L different block sizes for N transactions, 
        each requiring O(N X L) work, the total is O(L X N X L) = O(N X L^2).

        Worst case is O(N X L^3), where N is the number of transactions and L is the length of the signature, Worst case happens
        when the block size is 1, This is because the signature would have to be broken into L number of blocks, and the sorting
        cost would be in its worst case which is O(L^2), making the signature processing O(L^2) per transaction. Since we try L different
        block sizes for N transactions, with the worst case requiring O(N x L^2) work, the total is O(L X N X L^2) = O(N X L^3).
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
        Calculate suspicion score for a given block size using hash table for grouping.
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
        Create canonical form by extracting blocks, sorting them, and appending remaining chars.
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
        best_function = None
        best_mpcl = float('inf')
        
        for i in range(len(functions)):
            hash_function = functions[i]
            mpcl = self.calculate_max_probe_chain_length(hash_function)
            
            if mpcl < best_mpcl:
                best_mpcl = mpcl
                best_function = hash_function
        
        return (best_function, best_mpcl)

    def calculate_max_probe_chain_length(self, hash_function):
        hash_values = ArrayR(len(self.transactions))
        max_hash = 0
        
        for i in range(len(self.transactions)):
            hash_val = hash_function(self.transactions[i])
            hash_values[i] = hash_val
            if hash_val > max_hash:
                max_hash = hash_val
        
        table_size = max_hash + 1
        
        if table_size < len(self.transactions):
            return table_size
        
        hash_counts = ArrayR(table_size)
        for i in range(table_size):
            hash_counts[i] = 0
        
        for i in range(len(self.transactions)):
            hash_counts[hash_values[i]] += 1
        
        return self.simulate_worst_case_probing(hash_counts, table_size)
    
    def simulate_worst_case_probing(self, hash_counts, table_size):
        max_probe_length = 0
        
        max_probe_length = max(max_probe_length, 
                            self.simulate_insertion_order(hash_counts, table_size, "sequential"))
        
        max_probe_length = max(max_probe_length, 
                            self.simulate_insertion_order(hash_counts, table_size, "reverse"))
        
        return max_probe_length

    def simulate_insertion_order(self, hash_counts, table_size, order):
        table = ArrayR(table_size)
        for i in range(table_size):
            table[i] = False

        max_probe_length = 0

        num_positions_with_items = 0
        for pos in range(table_size):
            if hash_counts[pos] > 0:
                num_positions_with_items += 1

        positions = ArrayR(num_positions_with_items)
        pos_index = 0
        for pos in range(table_size):
            if hash_counts[pos] > 0:
                positions[pos_index] = pos
                pos_index += 1

        if order == "reverse":
            indices = range(num_positions_with_items - 1, -1, -1)
        else:
            indices = range(num_positions_with_items)

        for i in indices:
            pos = positions[i]
            for _ in range(hash_counts[pos]):
                actual_pos = pos
                probe_length = 0
                start_pos = actual_pos

                while table[actual_pos]:
                    actual_pos = (actual_pos + 1) % table_size
                    probe_length += 1
                    if actual_pos == start_pos:
                        return table_size

                max_probe_length = max(max_probe_length, probe_length)
                table[actual_pos] = True

        return max_probe_length
        
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