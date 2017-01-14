-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;

entity DataPath IS
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
END entity;

architecture impl of DataPath IS
  type Cards8 is array(7 downto 0) of STD_LOGIC_VECTOR(3 downto 0); -- create an array of 8 elements for the dealer and players hands

  signal DealtCards : Cards8 := ("0000","0000","0000","0000","0000","0000","0000","0000");

  signal CardSlot : STD_LOGIC_VECTOR(2 downto 0);
  signal RandomCard : std_logic_vector(3 downto 0);

  signal sig_dealerCards, sig_playerCards: std_logic_vector(15 downto 0);
  signal dealerScore, playerScore : std_logic_vector(4 downto 0);
  signal intDealerScore, intPlayerScore : integer;

  component dealcard
    port (clk : in std_logic;
          rst : in std_logic;
          card : out std_logic_vector(3 downto 0)
    );
  end component;
  component scorehand
  port ( hand : in std_logic_vector( 15 downto 0);
         score : out std_logic_vector(4 downto 0);
         stand : out std_logic;
         bust : out std_logic);
end component;

begin

  CardSlot <= dealTo & dealToCardSlot;
  CardDealer : dealcard port map (clk=>clock, rst=>reset, card=>RandomCard);

  process(clock, reset) begin
    if (reset = '1') then
      DealtCards <= ("0000","0000","0000","0000","0000","0000","0000","0000");
    elsif rising_edge(clock) then
      if deal = '1' then
        DealtCards(to_integer(unsigned(CardSlot))) <= RandomCard;
      end if;
    end if;
  end process;
 
  sig_dealerCards <= DealtCards(3) & DealtCards(2) & DealtCards(1) & DealtCards(0);
  sig_playerCards <= DealtCards(7) & DealtCards(6) & DealtCards(5) & DealtCards(4); 

  dealerCards <= sig_dealerCards;
  playerCards <= sig_playerCards;

  DScoreHand : scorehand port map (hand=>sig_dealerCards, score=>dealerScore, stand=>dealerStands, bust=>dealerBust);
  PScoreHand : scorehand port map (hand=>sig_playerCards, score=>playerScore, stand=>open, bust=>playerBust);

  intDealerScore <= to_integer(unsigned(dealerScore));
  intPlayerScore <= to_integer(unsigned(playerScore));

  playerWins <= '1' when ((intPlayerScore >  intDealerScore) and (intPlayerScore <= 21)) else '0';
  dealerWins <= '1' when ((intPlayerScore <= intDealerScore) and (intDealerScore <= 21)) else '0';
 
end impl;