-- synthesis VHDL_INPUT_VERSION VHDL_2008
-- pragma translate_off
library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity datapath_tb is
end entity;


architecture test of datapath_tb is

	component DataPath IS
	  PORT(
	   clock : IN STD_LOGIC;
	   reset : IN STD_LOGIC;

	   deal          : IN STD_LOGIC;
	   dealTo        : IN STD_LOGIC; -- 0 is dealer, 1 is player
	   dealToCardSlot: IN STD_LOGIC_VECTOR(1 downto 0);

	   playerCards : OUT STD_LOGIC_VECTOR(15 DOWNTO 0); -- player’s hand
	   dealerCards : OUT STD_LOGIC_VECTOR(15 DOWNTO 0); -- dealer’s hand

	   dealerStands : OUT STD_LOGIC; -- true if dealerScore >= 17

	   playerWins : OUT STD_LOGIC; -- true if playerScore >  dealerScore AND playerScore <= 21
	   dealerWins : OUT STD_LOGIC; -- true if dealerScore >= playerScore AND dealerScore <= 21

	   playerBust : OUT STD_LOGIC; -- true if playerScore > 21
	   dealerBust : OUT STD_LOGIC  -- true if dealerScore > 21
	  );
	END component;

  signal clock, reset, deal, dealTo, dealerStands, playerWins, dealerWins, playerBust, dealerBust : std_logic;
  signal dealToCardSlot : STD_LOGIC_VECTOR(1 downto 0);
  signal playerCards, dealerCards : STD_LOGIC_VECTOR(15 downto 0);

begin
	
	DUT: DataPath port map (clock, reset, deal, dealto, dealtocardslot, playercards, dealercards, dealerstands, playerwins, dealerwins, playerbust, dealerbust);
	process begin
		clock <= '0'; wait for 5 ns;
		clock <= '1'; wait for 5 ns;
	  -- clock <= '0'; wait for 5 ns;
	end process;
	process begin
	  -- asyncronous reset
	  reset <= '0';
	  wait for 2 ns;
	  reset <= '1';
	  wait for 2 ns;
	  reset <= '0';
	  wait for 6 ns;
    
    wait for 30 ns;
    
    deal <= '1';
    dealto <= '0';
    dealtocardslot <= "01";
    wait for 10 ns;
    
    
    wait for 10 ns;
		stop(0);
	end process;
end test;
-- pragma translate_on
