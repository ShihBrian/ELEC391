-- synthesis VHDL_INPUT_VERSION VHDL_2008
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;


package state_pkg is
	subtype state_encoding is STD_LOGIC_VECTOR(4 downto 0);

	constant SBegin   : state_encoding := "00000";

	constant SPlayer1 : state_encoding := "00001";
	constant SDealer1 : state_encoding := "00010";


	constant SPlayer2 : state_encoding := "00011";
	constant SPlayer3 : state_encoding := "00100";
	constant SPlayer4 : state_encoding := "00101";

	constant SDealer2 : state_encoding := "00110";
	constant SDealer3 : state_encoding := "00111";
	constant SDealer4 : state_encoding := "01000";

	constant SWinner  : state_encoding := "01001";
	constant SPWin    : state_encoding := "01010";
	constant SDWin    : state_encoding := "01011";
	Constant STie     : state_encoding := "01100";

	subtype state_output is STD_LOGIC_VECTOR(5 downto 0);
--                                     deal  dealto cardslot ledr  ledg
	constant OBegin    : state_output := "0" & "0" &  "00" &   "0" & "0";
	constant OPlayer1  : state_output := "1" & "1" &  "00" &   "0" & "0";
	constant ODealer1  : state_output := "1" & "0" &  "00" &   "0" & "0";

	constant OPlayer2  : state_output := "1" & "1" &  "01" &   "0" & "0";
	constant OPlayer3  : state_output := "1" & "1" &  "10" &   "0" & "0";
	constant OPlayer4  : state_output := "1" & "1" &  "11" &   "0" & "0";


	constant ODealer2  : state_output := "1" & "0" &  "01" &   "0" & "0";
	constant ODealer3  : state_output := "1" & "0" &  "10" &   "0" & "0";
	constant ODealer4  : state_output := "1" & "0" &  "11" &   "0" & "0";

	constant OWinner   : state_output := "0" & "0" &  "00" &   "0" & "0";
	constant OPWin     : state_output := "0" & "0" &  "00" &   "0" & "1";
	constant ODWin     : state_output := "0" & "0" &  "00" &   "1" & "0";
	constant OTie      : state_output := "0" & "0" &  "00" &   "1" & "1";
	constant OPause    : state_output := "0" & "0" &  "00" &   "-" & "-";
end package;




LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use work.state_pkg.all;


entity FSM is
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
end entity;

architecture impl of FSM is
	signal cur : state_encoding := SBegin;
	signal nxt : state_encoding;
	signal prev : state_encoding;
	signal SOUT : state_output := OBegin;
	--signal adv_sout : state_output;
	signal advance, oldNextStep: std_logic;
	-- signal deal_once: std_logic;
begin

  -- flip flop for the triggered rising edge clk
  process(clock, reset) begin
    if reset = '1' then
    	cur <= SBegin;
    elsif rising_edge(clock) then
    	if nextStep = '1' then 
    		if oldNextStep = '0' then -- key0 was just pressed
    			advance <= '1';
    			prev <= cur;
    			cur <= nxt; -- advance the state, since there are no "sub-states" just straight up advance state
    		else -- key0 has been held down
    			advance <= '0';
    			
    		end if;
    	else -- key0 isnt being pressed so we revert nextStep back to 0
    		
    		advance <= '0';
    	end if;
    	oldNextStep <= nextStep; -- update keyclk flag signal.
    end if;
  end process;

  -- main state logic
	process(all) begin
			case cur is
				when SBegin => nxt <= SPlayer1;

				when SPlayer1 => nxt <= SDealer1;

				when SDealer1 => nxt <= SPlayer2;

				when SPlayer2 =>
					if playerStands = '1' then
						nxt <= SDealer2;
					else
						nxt <= SPlayer3;
					end if;

				when SPlayer3 =>
					if playerStands = '1' then 
						nxt <= SDealer2;
					elsif playerBust = '1' then
						nxt <= SDealer2;
					else
						nxt <= SPlayer4;
					end if;

				when SPlayer4 => nxt <= SDealer2;

				when SDealer2 =>
					if dealerStands = '1' then
						nxt <= SWinner;
					else
						nxt <= SDealer3;
					end if;

				when SDealer3 =>
					if dealerStands = '1' then
						nxt <= SWinner;
					elsif dealerBust = '1' then
						nxt <= SWinner;
					else
						nxt <= SDealer4;
					end if;

				when SDealer4 => nxt <= SWinner;

				when SWinner =>
					if playerBust = '1' then -- player bust
						if dealerBust = '1' then -- player AND dealer bust
							nxt <= STie;
						else -- only player bust
							nxt <= SDWin;
						end if;
					elsif dealerbust = '1' then -- just dealer bust
						nxt <= SPWin;
					elsif playerWins = '1' then -- player win, noone bust
						nxt <= SPWin;
					else -- dealer win, noone bust
						nxt <= SDWin;
					end if;
				
				when SPWin => nxt <= SPwin;
				when SDWin => nxt <= SDwin;
				when STie  => nxt <= STie;
				when others => nxt <= SBegin;
			end case;
	end process;

	-- output logic
	process(cur) begin
		case cur is
			when SBegin => SOUT <= OBegin;
			when SPlayer1 => SOUT <= OPlayer1;
			when SDealer1 => SOUT <= ODealer1;
			when SPlayer2 => SOUT <= OPlayer2;
			when SPlayer3 => SOUT <= OPlayer3;
			when SPlayer4 => SOUT <= OPlayer4;
			when SDealer2 => SOUT <= ODealer2;
			when SDealer3 => SOUT <= ODealer3;
			when SDealer4 => SOUT <= ODealer4;
			when SWinner  => SOUT <= OWinner;
			when SPWin    => SOUT <= OPWin;
			when SDWin 		=> SOUT <= ODWin;
			when STie     => SOUT <= OTie;
			when others   => SOUT <= OBegin;
		end case;
	end process;

	-- show states on leds instead
	--redLEDs(4 downto 0) <= nxt;
	--greenLEDs(4 downto 0) <= cur;
	redLEDS <= (others => '1') when SOUT(1) = '1' else (others => '0');
	greenLEDs <= (others => '1') when SOUT(0) = '1' else (others => '0');
	
	
	deal <= SOUT(5) when (advance = '1' and prev /= cur
							and (unsigned(cur)) >= (unsigned(SPlayer1))
							and (unsigned(cur)) <= (unsigned(SDealer4))) else '0';
	--we only want to deal the card to slot once, not cycle through options and on the correct states.

	dealTo <= SOUT(4);
	dealToCardSlot <= SOUT(3 downto 2);

end impl;