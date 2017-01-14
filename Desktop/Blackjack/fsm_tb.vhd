-- synthesis VHDL_INPUT_VERSION VHDL_2008
-- pragma translate_off
library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity fsm_tb is
end entity;


architecture test of fsm_tb is
 
    component FSM is
    PORT(
		clk : IN STD_LOGIC;
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
	end component;
 
	signal clk, reset, nextStep, playerstands, dealerstands, playerwins, dealerwins, playerbust, dealerbust, deal, dealTo : std_logic;
	signal dealToCardSlot : std_logic_vector(1 downto 0);
	signal redLEDS : STD_LOGIC_VECTOR(17 DOWNTO 0);
	signal greenLEDs : STD_LOGIC_VECTOR(7 DOWNTO 0);
	
	begin
	  
		DUT : FSM port map(clk => clk, 
	                            reset => reset, 
	                            nextStep => nextStep, 
	                            playerStands => playerStands, 
	                            dealerstands => dealerstands, 
	                            playerwins => playerwins, 
	                            dealerwins => dealerwins, 
	                            playerbust => playerbust, 
	                            dealerbust => dealerbust,  
	                            deal => deal, 
	                            dealTo => dealTo, 
	                            dealToCardSlot => dealToCardSlot, 
	                            redLEDs => redLEDs, 
	                            greenLEDs => greenLEDs);
	    
	process begin
	  clk <= '1';
	  wait for 5 ns;
	  clk <= '0';
	  wait for 5 ns;
	end process;
	  
	process begin
	  nextStep <= '1';
	  reset <= '0';
	  wait for 3 ns;
	  reset <= '1';
	  wait for 3 ns;
	  reset <= '0';
    wait for 3 ns;


    wait for 1 ns;
    wait for 10 ns;
    wait for 10 ns;
    wait for 10 ns;
    wait for 10 ns;
    wait for 10 ns;
    wait for 10 ns;
    wait for 10 ns;
    stop(0);
       
    end process;
     
end architecture;
-- pragma translate_on