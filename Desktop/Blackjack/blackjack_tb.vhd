-- synthesis VHDL_INPUT_VERSION VHDL_2008
-- pragma translate_off
library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity blackjack_tb is
end entity;

architecture test of blackjack_tb is
 
	component BlackJack
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
	END component;
 
	signal clk : std_logic;
	signal key : std_logic_vector(3 downto 0) := "1111";
	signal sw : std_logic_vector(0 downto 0);
	signal ledr : std_logic_vector(17 downto 0);
	signal ledg : std_logic_vector(7 downto 0);

	signal hex7, hex6, hex5, hex4, hex3, hex2, hex1, hex0 : std_logic_vector(6 downto 0);
	
	begin
	  
		DUT : BlackJack port map(CLOCK_50=>clk,
															sw=>sw,
															key=>key,
															ledr=>ledr,
															ledg=>ledg,
															hex7=>hex7, hex6=>hex6, hex5=>hex5, hex4=>hex4,
															hex3=>hex3, hex2=>hex2, hex1=>hex1, hex0=>hex0);
	    
	process begin
	  clk <= '0';
	  wait for 5 ns;
	  clk <= '1';
	  wait for 5 ns;
	end process;

	process begin
		key(0) <= '1';
		wait for 23 ns;
		key(0) <= '0';
		wait for 31 ns;
		key(0) <= '1';
		wait for 9 ns;
		key(0) <= '0';
		wait for 7 ns;
	end process;
	 
	process begin
		sw(0) <= '0';
	  key(3) <= '1';
	  wait for 3 ns;
	  key(3) <= '0';
	  wait for 3 ns;
	  key(3) <= '1';
    wait for 3 ns;


    wait for 1 ns;
    wait for 500 ns;
    stop(0);
       
    end process;
     
end architecture;

-- pragma translate_on