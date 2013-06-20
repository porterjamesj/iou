# iou

iou is a command line tool for managing debts (for things like
communally purchased food, bills, etc.) in small groups of people. My
roommates and I use it to keep track of who owes who how much without
going insane.

## Installation

iou is a python script with no external dependencies. You do need to
have the json module, which means python version 2.6 or greater.
	
    $ git clone https://github.com/porterjamesj/iou.git
	$ python setup.py install
	
## Usage

Typing `iou -h` will get you a concise summary

The first thing you need to do is initialize the file that iou uses to
keep track of debts with the names of the relevant people

	$ iou init alice bob charlie
	
This will create `~/.iou` which is just a JSON file that iou
serializes to, and populate it with the names alice, bob, and charlie.

	$ iou view
	No debts owed to charlie

	No debts owed to bob
	
	No debts owed to alice

	
Nobody owes anybody else money to start out with. Imagine that Alice
and Charlie go out to eat, Charlie forgets to bring any money, and
Alice pays for his $10 dinner. We can add this debt with the `add` command.

	$ iou add alice 10 charlie

The syntax here is `iou add [creditor] [amount] [debtor]`. Now if we
view the debts with the `view` command:

	$ iou view
	No debts owed to charlie

	No debts owed to bob
	
	alice <-+-- charlie: 10.0
	
It prints a nice graphical summary of all the debts. Let's let a few
more debts accumulate:

	$ iou add alice 5 bob
	$ iou add charlie 20 bob
	$ iou add bob 10 charlie
	$ iou view
	charlie <-+-- bob: 20.0

	bob <-+-- charlie: 10.0
	
	alice <-+-- charlie: 10.0
		    |
			+-- bob: 5.0
	
	
Nice! But this graph has a lot of needless money changing hands. For
example, why should Charlie have to find Bob and give him $10 only to
have Bob give him $20 right back? It would be simpler for Bob to just
owe Charlie $10. Moreover, since Charlie owes $10 to Alice anyway, it
would be simpler for Bob to owe that $10 to Charlie directly.
Fortunately, iou handles all this automatically with the `cleanup`
command.

	$ iou cleanup
	$ iou view
	No debts owed to charlie

	No debts owed to bob
	
	alice <-+-- bob: 15.0
	
Ahh, much better. Notice that everyone still nets the same amount of
money gained or lost, but the structure is much simpler so there's
less hassle for all. Having things automatically simplified in this
manner is the killer feature of doing this with software.

Now let's say Bob pays back Alice $10 of what he owes her. We handle this
with the `remove` command.

	$ iou remove alice 10 bob
	$ iou view
	No debts owed to charlie

	No debts owed to bob

	alice <-+-- bob: 5.0
	
Cool. Now let's say he pays back everything he owes her. We can use

	$ iou forgive alice bob
	
To clear the entirety of the debt from Bob to Alice, regardless of it's amount.

# Sugar

Imagine that the three go to a movie and Alice buys some $7
popcorn for Bob and Charlie to share. We can add this as:

	$ iou add alice 7 bob charlie
	$ iou view
	No debts owed to charlie

	No debts owed to bob
	
	alice <-+-- charlie: 3.5
		    |
			+-- bob: 3.5
			
You can specify an arbitrary number of debtors and iou will handle the
split correctly. As another example, let's say Bob buys a videogame
that all three of them will use:

	$ iou add bob 60 alice bob charlie
	$ iou view
	No debts owed to charlie

	bob <-+-- charlie: 20.0
		  |
		  +-- alice: 20.0

	alice <-+-- charlie: 3.5
			|
			+-- bob: 3.5

If there a lot of debts beings split between all parties, typing
everyone's name out after each addition gets pretty laborious, so as a
shortcut you can use:

	$ iou add bob 60 all
	
`all` is expanded into the names of everyone in the graph.

You can also specify that a debt is owed from all but certain
individuals. For example, if Bob buys some eggs for the group, but
Alice is vegan so she won't be using any, you could do this:

	$ iou add 2.95 all but alice
	
`all but alice` is expanded into the names of everyone in the graph
except Alice. An arbitrary number of names can come after `but`. In
this case, since we only have three people, `all but alice` is just
`bob charlie` so this is actually longer to type, but when dealing
with bigger groups the `but` sugar can be very helpful.

## Batch processing

A typical way of using iou is to have everyone save their recipts
from communal purchases, batch process them all every few
weeks/months, and cleanup the resulting graph to see who owes who how
much. Typing in all those `add` commands one at a time can be a pain
though, so iou supports batch processing of debt additions. You can
type up all the debts in a file like so:

	alice 20 bob
	bob 4.35 all
	bob 5 all but charlie
	charlie 67 all
	
Essentially just as if you were to type it in on the command line but
without the `iou add` at the beginning. Imagine the above is saved in a file
called `debts.txt.`. We can process it with:

	$ iou process debts.txt
	$ iou view
	charlie <-+-- bob: 22.3333333333
          |
          +-- alice: 22.3333333333

	bob <-+-- charlie: 1.45
		  |
		  +-- alice: 3.95

	alice <-+-- bob: 20.0
	
And then clean it up:	

	$ iou cleanup
	$ iou view
	charlie <-+-- bob: 36.9333333333
          |
          +-- alice: 6.28333333333

	No debts owed to bob

	No debts owed to alice
	
Cool. 

## Adding and removing people

Imagine that the three get two new roommates, David and Elise.
We can add them to the graph like so:

	$ iou newpeople david elise
	$ iou view
	No debts owed to elise

	No debts owed to bob

	No debts owed to david

	No debts owed to alice

	charlie <-+-- bob: 36.9333333333
			  |
			  +-- alice: 6.28333333333
			  
And then maybe Bob moves out:

	$ iou rmpeople bob
	No debts owed to elise

	charlie <-+-- alice: 6.28333333333

	No debts owed to alice

	No debts owed to david
	
## License

MIT