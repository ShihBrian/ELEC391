-- synthesis VHDL_INPUT_VERSION VHDL_2008
-- pragma translate_off
library ieee;
use ieee.std_logic_1164.all;

entity scorehand_tb is
end entity;


architecture stimulus of scorehand_tb is

	--Declare the device under test (DUT)
	component scorehand is
  port ( hand : in std_logic_vector( 15 downto 0);
         score : out std_logic_vector(4 downto 0);
         stand : out std_logic;
         bust : out std_logic);
	end component;

  signal hand : std_logic_vector(15 downto 0);
  signal score : std_logic_vector(4 downto 0);
  signal stand, bust : std_logic;
  constant PERIOD : time := 5ns;
begin
	
	DUT: scorehand port map (hand, score, stand, bust);
	  process begin
	     
	   hand <= "0100001000010010"; --9
	   wait for PERIOD;
	   
	   hand <= "0000000000010001"; -- 12 
	   wait for PERIOD;
	   
	   hand <= "0001000100010001"; -- 14
	   wait for PERIOD;
	   
	   hand <= "0001000100011000"; -- 21
	   wait for PERIOD;
	   
	   hand <= "0000" & "0000" & "0000" & "0000"; -- empty hand
	   wait for PERIOD;
	   
	   hand <= "1100" & "0001" & "1101" & "0001"; -- bust
	   wait for PERIOD;
	   
	   hand <= "1100" & "0001" & "0001" & "0001";
	   wait for PERIOD;
	   
	   wait;
	   end process;
end stimulus;
--pragma translate_on
