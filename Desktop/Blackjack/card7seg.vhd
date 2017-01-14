-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;

entity card7seg is
        PORT(
	   	card : IN  STD_LOGIC_VECTOR(3 DOWNTO 0); -- value of card
	   	seg7 : OUT STD_LOGIC_VECTOR(6 DOWNTO 0)  -- 7-seg LED pattern
	     );
end entity;

architecture impl of card7seg is
begin

   process (card) begin
        case card is
           when "0000" => seg7 <= "1111111";
           when "0001" => seg7 <= "0001000"; -- A
           when "0010" => seg7 <= "0100100";
           when "0011" => seg7 <= "0110000";
           when "0100" => seg7 <= "0011001";
           when "0101" => seg7 <= "0010010";
           when "0110" => seg7 <= "0000010";
           when "0111" => seg7 <= "1111000";
           when "1000" => seg7 <= "0000000";
           when "1001" => seg7 <= "0010000";
           when "1010" => seg7 <= "1000000";
           when "1011" => seg7 <= "1100000"; -- J
           when "1100" => seg7 <= "0011000"; -- Q
           when "1101" => seg7 <= "0001001"; -- K
           when others => seg7 <= "1011010";
         end case;
    end process;
end architecture;