library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity lab5 is
  port(CLOCK_50            : in  std_logic;
       KEY                 : in  std_logic_vector(3 downto 0);
       SW                  : in  std_logic_vector(17 downto 0);
       VGA_R, VGA_G, VGA_B : out std_logic_vector(9 downto 0);  -- The outs go to VGA controller
       VGA_HS              : out std_logic;
       VGA_VS              : out std_logic;
       VGA_BLANK           : out std_logic;
       VGA_SYNC            : out std_logic;
       VGA_CLK             : out std_logic);
end lab5;

architecture RTL of lab5 is
  component vga_adapter
    generic(RESOLUTION : string);
    port (resetn                                       : in  std_logic;
          clock                                        : in  std_logic;
          colour                                       : in  std_logic_vector(2 downto 0);
          x                                            : in  std_logic_vector(7 downto 0);
          y                                            : in  std_logic_vector(6 downto 0);
          plot                                         : in  std_logic;
          VGA_R, VGA_G, VGA_B                          : out std_logic_vector(9 downto 0);
          VGA_HS, VGA_VS, VGA_BLANK, VGA_SYNC, VGA_CLK : out std_logic);
  end component;
  component fsmdata
		port(clk : in std_logic;
				 rst : in std_logic;
         sw : in std_logic_vector(17 downto 0);
				plot : out std_logic;
				colour : out std_logic_vector(2 downto 0);
			 	xcoord : out std_logic_vector(7 downto 0);
			 	ycoord : out std_logic_vector(6 downto 0));

  end component;
  
  signal not_key3 : std_logic;
  signal colour : std_logic_vector(2 downto 0);
  signal x : std_logic_vector(7 downto 0);
  signal y : std_logic_vector(6 downto 0);
  signal plot : std_logic;
  
  
begin

 not_key3 <= not key(3);

  vga_u0 : vga_adapter
    generic map(RESOLUTION => "160x120") 
    port map(resetn    => KEY(3),
             clock     => CLOCK_50,
             colour    => colour,
             x         => x,
             y         => y,
             plot      => plot,
             VGA_R     => VGA_R,
             VGA_G     => VGA_G,
             VGA_B     => VGA_B,
             VGA_HS    => VGA_HS,
             VGA_VS    => VGA_VS,
             VGA_BLANK => VGA_BLANK,
             VGA_SYNC  => VGA_SYNC,
             VGA_CLK   => VGA_CLK);
	
	the_fsmdata : fsmdata
		port map(clk => CLOCK_50,
					rst => not_key3,
          sw => SW,
					plot => plot,
					colour => colour,
					xcoord => x,
					ycoord => y);
					


end RTL;


