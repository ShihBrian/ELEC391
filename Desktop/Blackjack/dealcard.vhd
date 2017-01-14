-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity dealcard is
  port (clk : in std_logic;
        rst : in std_logic;
--         CLOCK_50 : in std_logic;
--         ledg : out std_logic_vector(3 downto 0);
--         KEY : in std_logic_vector(3 downto 0);
         card : out std_logic_vector(3 downto 0));

end entity;

architecture impl of dealcard is
  signal counter : unsigned(3 downto 0) := "0001";
begin
  
  process(clk, rst) begin
    if (rst = '1') then
      counter <= "0001";
    elsif rising_edge(clk) then
      counter <= counter + 1;
    end if;
    if( counter = 14 ) then
      counter <= "0001";
    end if;
  end process;
  
  card <= std_logic_vector(counter);


  --process( KEY(0) ) begin
  --  if falling_edge(KEY(0)) then
  --    case std_logic_vector(counter) is
  --      when "0001" => ledg <= "0001";
  --      when "0010" => ledg <= "0010";
  --      when "0011" => ledg <= "0011";
  --      when "0100" => ledg <= "0100";
  --      when "0101" => ledg <= "0101";
  --      when "0110" => ledg <= "0110";
  --      when "0111" => ledg <= "0111";
  --      when "1000" => ledg <= "1000";
  --      when "1001" => ledg <= "1001";
  --      when "1010" => ledg <= "1010";
  --      when "1011" => ledg <= "1011";
  --      when "1100" => ledg <= "1100";
  --      when "1101" => ledg <= "1101";
  --      when others => ledg <= "1111";
  --    end case;
  --  end if;
  --end process;
end architecture;
