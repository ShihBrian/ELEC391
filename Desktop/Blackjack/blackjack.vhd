-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;

ENTITY BlackJack IS
        -- Do not modify this port list! 
	PORT(
		CLOCK_50 : in std_logic; -- A 50MHz clock
		SW   : in  std_logic_vector(0 downto 0);  -- SW(0) = player stands
		KEY  : in  std_logic_vector(3 downto 0);  -- KEY(3) reset, KEY(0) advance
		LEDR : out std_logic_vector(17 downto 0); -- red LEDs: dealer wins
		LEDG : out std_logic_vector(7 downto 0);  -- green LEDs: player wins

		HEX7 : out std_logic_vector(6 downto 0);  -- dealer, fourth card
		HEX6 : out std_logic_vector(6 downto 0);  -- dealer, third card
		HEX5 : out std_logic_vector(6 downto 0);  -- dealer, second card
		HEX4 : out std_logic_vector(6 downto 0);  -- dealer, first card

		HEX3 : out std_logic_vector(6 downto 0);  -- player, fourth card
		HEX2 : out std_logic_vector(6 downto 0);  -- player, third card
		HEX1 : out std_logic_vector(6 downto 0);  -- player, second card
		HEX0 : out std_logic_vector(6 downto 0)   -- player, first card
	);
END;

ARCHITECTURE Behavioural OF BlackJack IS

	COMPONENT Card7Seg IS
	PORT(
	   	card : IN  STD_LOGIC_VECTOR(3 DOWNTO 0); -- value of card
	   	seg7 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)  -- 7-seg LED pattern
	);
	END COMPONENT;

	COMPONENT DataPath IS
	PORT(
		clock : IN STD_LOGIC;
		reset : IN STD_LOGIC;

		deal          : IN STD_LOGIC;
		dealTo        : IN STD_LOGIC;
		dealToCardSlot: IN STD_LOGIC_VECTOR(1 downto 0);

		playerCards : OUT STD_LOGIC_VECTOR(15 DOWNTO 0); -- player’s hand
		dealerCards : OUT STD_LOGIC_VECTOR(15 DOWNTO 0); -- dealer’s hand

		dealerStands : OUT STD_LOGIC; -- true if dealerScore >= 17

		playerWins : OUT STD_LOGIC; -- true if playerScore >  dealerScore AND playerScore <= 21
		dealerWins : OUT STD_LOGIC; -- true if dealerScore >= playerScore AND dealerScore <= 21

		playerBust : OUT STD_LOGIC; -- true if playerScore > 21
		dealerBust : OUT STD_LOGIC  -- true if dealerScore > 21
	);
	END COMPONENT;

	COMPONENT FSM IS
	PORT(
		clock : IN STD_LOGIC;
		reset : IN STD_LOGIC;

		nextStep     : IN STD_LOGIC; -- when true, it advances game to next step
		playerStands : IN STD_LOGIC; -- true if player wants to stand
		dealerStands : IN STD_LOGIC; -- true if dealerScore >= 17
		playerWins   : IN STD_LOGIC; -- true if playerScore >  dealerScore AND playerScore <= 21
		dealerWins   : IN STD_LOGIC; -- true if dealerScore >= playerScore AND dealerScore <= 21
		playerBust   : IN STD_LOGIC; -- true if playerScore > 21
		dealerBust   : IN STD_LOGIC; -- true if dealerScore > 21

		deal          : OUT STD_LOGIC; -- when true, deal a card
                                               -- dealTo and dealToCardSlot are don’t care when deal is false
		dealTo        : OUT STD_LOGIC; -- when true, deal a card to player, otherwise, deal to dealer
		dealToCardSlot: OUT STD_LOGIC_VECTOR(1 downto 0); -- Card slot in the hand to deal to
		
		redLEDs   : OUT STD_LOGIC_VECTOR(17 DOWNTO 0);
		greenLEDs : OUT STD_LOGIC_VECTOR(7 DOWNTO 0)
	);
	END COMPONENT;


	signal playercards, dealercards : STD_LOGIC_VECTOR(15 downto 0);
	signal reset : std_logic;
	signal deal, dealto : STD_LOGIC;
	signal dealerstands, playerstands, playerbust, dealerbust, dealerwins, playerwins : STD_LOGIC;
	signal dealtocardslot : STD_LOGIC_VECTOR(1 downto 0);
	signal nextStep : std_logic;
	signal keyclk : std_logic;

BEGIN
        ---- Your code goes here!
	----

	reset <= not key(3);
	keyclk <= not key(0);


	The_Datapath : DataPath port map (clock=>CLOCK_50,
										reset=>reset,
										deal=>deal,
										dealTo=>dealto,
										dealToCardSlot=>dealtocardslot,
										playerCards=>playercards,
										dealerCards=>dealercards,
										dealerStands=>dealerstands,
										playerwins=>playerwins,
										dealerwins=>dealerWins,
										playerbust=>playerBust,
										dealerbust=>dealerbust);

	The_FSM : FSM port map (clock=>CLOCK_50,
								reset=>reset,
								nextStep=>keyclk,
								playerstands=>sw(0),
								dealerstands=>dealerstands,
								playerwins=>playerwins,
								dealerwins=>dealerwins,
								playerbust=>playerbust,
								dealerbust=>dealerbust,
								deal=>deal,
								dealto=>dealto,
								dealToCardSlot=>dealToCardSlot,
								redLEDs=>ledr,
								greenLEDs=>ledg);

	PCard1 : Card7Seg port map (PlayerCards(3 downto 0), HEX0);
	PCard2 : Card7Seg port map (PlayerCards(7 downto 4), HEX1);
	PCard3 : Card7Seg port map (PlayerCards(11 downto 8), HEX2);
	PCard4 : Card7Seg port map (PlayerCards(15 downto 12), HEX3);

	DCard1 : Card7Seg port map (DealerCards(3 downto 0), HEX4);
	DCard2 : Card7Seg port map (DealerCards(7 downto 4), HEX5);
	DCard3 : Card7Seg port map (DealerCards(11 downto 8), HEX6);
	DCard4 : Card7Seg port map (DealerCards(15 downto 12), HEX7);
	
END Behavioural;

