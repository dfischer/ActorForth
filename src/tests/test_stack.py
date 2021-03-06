import unittest

from itertools import repeat

from stack import KStack, Stack

class StackTests(unittest.TestCase):

    def setUp(self):
        self.init_list = ['A','B','C','D','E']
        self.result_list = [x for x in self.init_list] 
        self.depth_history = [x+1 for x in range(len(self.init_list))]
        self.depth_count_history = [x for x in zip(self.depth_history,repeat(1))]
        self.max_depth = len(self.init_list)


    def test_no_max_depth_in_a_fresh_stack(self) -> None:
        s = Stack()
        self.assertEqual(s.max_depth(), 0)


    def test_history_depth_limit(self):
        s = Stack()
        [s.push('X') for n in range(Stack.DEPTH_HISTORY * 2)]
        self.assertEqual(len(s.depth_history()), Stack.DEPTH_HISTORY)

        self.assertEqual(len(s.depth_history(Stack.DEPTH_HISTORY * 2)), Stack.DEPTH_HISTORY)

        self.assertEqual(len(s.depth_history(17)), 17)


    def test_history_depth_count_should_match_number_of_pushes(self):
        s = Stack()
        #import pdb; pdb.set_trace()
        self.assertEqual(s.history_depth_count(0),1)
        self.assertTrue(s.is_empty())
        self.assertEqual(s.contents(),[])

        for i, v in enumerate(self.init_list):
            s.push(v)

            expected = [1]*(i+2)+[0]*(len(self.init_list)-1)
            for depth in range(len(self.init_list)+1):
                self.assertEqual(s.history_depth_count(depth),expected[depth])

        depth_count = s.history_depth_count()
        self.assertEqual(s.contents(), [x for x in self.init_list])
        self.assertEqual(s.tos(),self.init_list[-1])
        self.assertEqual(depth_count,[(0,1),(1,1),(2,1),(3,1),(4,1),(5,1)])

        self.assertEqual(s.max_depth(), self.max_depth)

        self.assertEqual(s.total_operations(), len(self.init_list))

        empty = None
        while empty != KStack.Empty:
            empty = s.pop()

        self.assertEqual(s.total_operations(), len(self.init_list)*2)

    def test_stack_copy(self) -> None:
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)

        self.assertEqual(str(s.contents()),'[1, 2, 3]')

        r = s.copy()

        #print("Type s = %s, Type r = %s" % (type(s),type(r)))
        self.assertEqual(type(s),type(r))

        x = s.tos()
        y = r.tos()
        self.assertEqual(x,y)

        self.assertEqual(s.pop(), r.pop())
        self.assertEqual(s.pop(), r.pop())
        self.assertEqual(s.pop(), r.pop())

        self.assertEqual(len(s),len(s))

    def test_empty_stack_copy(self) -> None:
        s = Stack()
        self.assertEqual(str(s.contents()),'[]')

        r = s.copy()

        print("Type s = %s, Type r = %s" % (type(s),type(r)))

        x = s.tos()
        y = r.tos()
        self.assertEqual(x,y)
        self.assertEqual(len(s),0)
        self.assertEqual(len(r),0)

    def test_stack_equality(self) -> None:
        s = Stack()
        r = Stack()
        q = Stack()
        p = Stack()

        s.push(1)
        s.push(2)
        r.push(1)
        r.push(2)
        q.push(1)
        q.push(1)
        p.push(1)

        assert s == r
        assert s != q
        assert s != p

    def test_stack_full_content(self) -> None:
        s = Stack( self.init_list )
        assert s.contents() == self.init_list
        #assert str(s) == str(s.contents()) == s.__repr__()

    def test_stack_last_content(self) -> None:
        s = Stack( self.init_list )
        assert s.contents(4) == self.init_list[-4:]    

    def test_stack_underflow_content(self) -> None:
        s = Stack( self.init_list )
        l = len(self.init_list) + 1
        with self.assertRaises(Exception) as x:
            s.contents(l)

    def test_can_only_compare_to_stack(self) -> None:
        s = Stack( self.init_list )
        (s == self.init_list) == NotImplemented

class KevlinsStackTest(unittest.TestCase):
    """
    https://youtu.be/nrVIlhtoE3Y?t=3630

    FSM:

        EMPTY  ------- push(v) ------>  NON-EMPTY
         ^  |                            ^      |
         |__|  <------ pop [depth==1]-   |______|
        depth                              depth
                                           top
                                           push
                                           pop [depth>1]

    https://youtu.be/nrVIlhtoE3Y?t=4440                                           

    alphabet(Stack) = { push, pop, popped, empty, tos }

        EMPTY  ------- push(v) ------>  NON-EMPTY
         ^  |                            ^      |
         |__|  <------ pop/popped-----   |______|
        pop/empty                          push(v)
        tos/empty                          pop/popped
                                           tos/value
    
    empty() ->  
        receive
            {push, Top} -> non_empty(Top);
            {pop, Return} -> Return ! empty
        end,
        empty().

    non_empty(Value) ->
        receive
            {push, Top} ->
                non_empty(Top),
                non_empty(Value);
            {pop, Return} ->
                Return ! {popped, Value}
        end.
    """
    def setUp(self):
        self.stack = KStack()

    def push_some_data(self, list_of_data):
        [self.stack.push(x) for x in list_of_data]        

    def test_while_empty_pop_returns_empty(self):
        self.assertEqual(self.stack.pop(), KStack.Empty)

    def test_while_empty_tos_returns_empty(self):
        self.assertEqual(self.stack.tos(), KStack.Empty)

    def test_while_empty_push_returns_nonempty(self):
        self.assertEqual(self.stack.push(1), KStack.NonEmpty)

    def test_while_nonempty_pop_consumes_the_last_value_pushed(self):
        self.push_some_data([1,2,3,4])
        self.assertEqual(self.stack.pop(), 4)
        self.assertEqual(self.stack.pop(), 3)

    def test_while_nonempty_tos_returns_the_last_value_pushed(self):       
        self.push_some_data(['a','b','c']) 
        self.assertEqual(self.stack.tos(), 'c')
        self.assertEqual(self.stack.tos(), 'c')

    def test_while_nonempty_continued_pops_return_data_in_reverse_order(self):
        data = ['a','b',3,'c',KStack,0,17,-42]
        self.push_some_data(data)
        for d in reversed(data):
            self.assertEqual(d, self.stack.pop())

        self.assertEqual(self.stack.pop(), KStack.Empty)
        self.assertEqual(self.stack.tos(), KStack.Empty)

    def test_tos(self) -> None:
        self.assertEqual(self.stack.tos(), KStack.Empty)
        data = ['a', 'b']
        self.push_some_data(data)
        self.assertEqual(self.stack.tos(), 'b')
        self.stack.pop()
        self.assertEqual(self.stack.tos(), 'a')
        self.stack.pop()
        self.assertEqual(self.stack.tos(), KStack.Empty)
        

    def test_kstack_copy(self) -> None:
        s = KStack()
        s.push(1)
        s.push(2)
        s.push(3)

        r = s.copy()

        self.assertEqual(type(s),type(r))

        x = s.tos()
        y = r.tos()
        self.assertEqual(x,y)

        self.assertEqual(s.pop(), r.pop())
        self.assertEqual(s.pop(), r.pop())
        self.assertEqual(s.pop(), r.pop())

    def test_empty_kstack_copy(self) -> None:
        s = KStack()
        r = s.copy()

        print("Type s = %s, Type r = %s" % (type(s),type(r)))

        x = s.tos()
        y = r.tos()
        self.assertEqual(x,y)
