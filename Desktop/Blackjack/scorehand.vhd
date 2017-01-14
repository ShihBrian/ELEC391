-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity scorehand is
  port ( hand : in std_logic_vector( 15 downto 0);
         score : out std_logic_vector(4 downto 0);
         stand : out std_logic;
         bust : out std_logic);
end entity;

architecture impl of scorehand is
  --signals for testing
  --signal card1, card2, card3, card4 : std_logic_vector(3 downto 0);
  --signal ace1, ace11 : std_logic_vector(5 downto 0);
  --signal isace : std_logic;
  -- delete after
  
begin
    -- signals for testing purposes
    --card1 <= hand(3 downto 0);
    --card2 <= hand(7 downto 4);
    --card3 <= hand(11 downto 8);
    --card4 <= hand(15 downto 12);
    -- delete after
    
    
  process(all)
    variable first,second,third,fourth : unsigned(5 downto 0);
    variable ace : std_logic := '0';
    variable totalAce1, totalAce11, total : unsigned(5 downto 0);
  begin
    first  := unsigned("00" & hand( 3 downto  0));
    second := unsigned("00" & hand( 7 downto  4));
    third  := unsigned("00" & hand(11 downto  8));
    fourth := unsigned("00" & hand(15 downto 12));
    
    ace := '0';
    
    if first = "000001" then
      ace := '1';
    elsif to_integer(first) > 10 then
      first := "001010";
    end if;
  
    if second = "000001" then
      ace := '1';
    elsif to_integer(second) > 10 then
      second := "001010";
    end if;  
    
    if third = "000001" then
      ace := '1';
    elsif to_integer(third) > 10 then
      third := "001010";
    end if;
  
    if fourth = "000001" then
      ace := '1';
    elsif to_integer(fourth) > 10 then
      fourth := "001010";
    end if;    
    
    -- signals for testing
    --isace <= ace;
    -- delete after


    if ace = '1' then -- compute which value to use
      totalAce11 := unsigned(first + second + third + fourth + 10);
      totalAce1  := unsigned(first + second + third + fourth);

      -- signals for testing
      --ace11 <= std_logic_vector(totalAce11);
      --ace1 <= std_logic_vector(totalAce1);
      -- delete after

      if (to_integer(totalAce11) <= 21) then -- ace=11 <= 21
        if (to_integer(totalAce1) <= to_integer(totalAce11)) then -- ace=1 < ace=11 <= 21
          total := totalAce11;
        elsif to_integer(totalAce1) > 21 then -- ace=11 <= 21 < ace=1
          total := totalAce11;
        else -- ace=11 < ace=1 <= 21
          total := totalAce1;
        end if;
      else -- ace=11 > 21, use ace=1 value anyways.
        total := totalAce1;
      end if;

    else -- no ace
      total := unsigned(first + second + third + fourth);
    end if;
    
    if(to_integer(total) > 21) then -- >21, bust
      score <= "11111";
      bust <= '1';
      stand <= '0';
    elsif (to_integer(total) >= 17) then -- 17-21, AI Stand
      score <= std_logic_vector(total(4 downto 0));
      stand <= '1';
      bust <= '0';
    else -- <17, no status
      score <= std_logic_vector(total(4 downto 0));
      stand <= '0';
      bust <= '0';
    end if;
    
    
  end process;
end architecture;
