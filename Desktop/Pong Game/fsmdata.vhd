-- synthesis VHDL_INPUT_VERSION VHDL_2008

-- Name: Bo Hu, Brian Shih
-- Student Number: 32312126, 31601131

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fsmdata is
	port(clk : in std_logic;
			 rst : in std_logic;
			 sw : in std_logic_vector(17 downto 0);
			 plot : out std_logic;
			 colour : out std_logic_vector(2 downto 0);
			 xcoord : out std_logic_vector(7 downto 0);
			 ycoord : out std_logic_vector(6 downto 0)


			 );

end fsmdata;

architecture impl of fsmdata is
	type STATE is (SInitY, SInitX, SPlot, SDoneClr, SDrawBars, SDrawPads, SSlowClk, SWait,	ST1G, ST1F, ST2F, ST2G, SClearBall, SDrawBall);

	signal BallSlowClk : integer := 0;
	signal PaddleSlowClk : integer := 0;


	--  testing signals
	signal Tcur, Tprev, Tnxt : STATE;
begin
	



	main_process : process (all)
		variable cur, prev, nxt : STATE;
		variable x, y, Xcap, Ycap : integer;

		-- y boundaries of the board
		constant Ymin : integer := 29;
		constant Ymax : integer := 89;

		-- x cooridnates of the paddles
		constant T1GX : integer := 24;
		constant T1FX : integer := 69;
		constant T2FX : integer := 99;
		constant T2GX : integer := 134; --134

		constant Xmin : integer := 19;
		constant Xmax : integer := 140;

		variable T1Gtop, T1Ftop, T2Ftop, T2Gtop : integer := 54;
		variable T1Gbot, T1Fbot, T2Fbot, T2Gbot : integer := 63;

		variable dir : std_logic;

		variable paddle_clk, ball_clk: integer := 0;
		variable Ballx : integer := 80;
		variable Bally : integer := 60;
		variable dx : integer := 0; 
		variable dy : integer := 1;
		variable speed_cnt : integer := 0;              ------
		variable ball_speed : integer := 10000000;      -------
		variable paddle_speed : integer;

	begin
		if rst = '1' then
			cur := SInitY;

			T1Gtop := 54;
			T1Ftop := 54;
			T2Ftop := 54;
			T2Gtop := 54;

			T1Gbot := 63;
			T1Fbot := 63;
			T2Fbot := 63;
			T2Gbot := 63;

			paddle_clk := 0;
			
			Ballx := 80;
			Bally := 60;
			dx := 1;
			dy := 1;
			speed_cnt := 0;                      -------
			ball_speed := 10000000;              --------
      paddle_speed := 10000000;


		elsif rising_edge(clk) then
			-- testing singals
		  Tcur <= cur;
	    Tprev <= prev;

			if cur = SInitY then
				y := 0;
				x := 0;
				nxt := SInitX;


			elsif cur = SInitX then
				x := x + 1;
				y := 0;
				if x = 160 then
					nxt := SDoneclr;
				else
					nxt := SPlot;
				end if;


			elsif cur = SPlot then
				y := y + 1;
				if y = 119 then
					nxt := SInitX;
				else
					nxt := SPlot;
				end if;
				plot <= '1';
				colour <= "000";


			elsif cur = SDoneclr then
				plot <= '0';
				nxt := SDrawBars;

			elsif cur = SDrawBars then
				nxt := SDrawBars;
				if prev = SDoneClr then
					y := Ymin;
					x := Xmin;
				else
					x :=  x + 1;
				end if;

				if x = Xmax then
					if y = Ymin then
						y := Ymax;
						x := Xmin;
					else
						nxt := SDrawPads;
					end if;
				end if;

				plot <= '1';
				colour <= "111";

			elsif cur = SDrawPads then
				nxt := SDrawPads;
				if prev = SDrawBars then
					x := T1GX;
					y := 54;
					colour <= "001";
				else
					y := y + 1;
				end if;
				-- done drawing a paddle
				if y = 64 then
					y := 54;
					-- done T1G
					if x = T1GX then
						x := T1FX;
					-- done T1F
					elsif x = T1FX then
						colour <= "100";
						x := T2FX;
					-- T2F
					elsif x = T2FX then
						x := T2GX;
					-- T2G
					else
						nxt := SSlowClk;
					end if;
				end if;
				plot <= '1';

			elsif cur = SSlowClk then
				plot <= '0';
				paddle_clk := paddle_clk + 1;
				ball_clk := ball_clk + 1;
				if ball_clk >= ball_speed then
					ball_clk := 0;
					nxt := SClearBall;
				elsif paddle_clk >= paddle_speed then        -- changed to lower number, feels better at this speed 
					paddle_clk := 0;
					nxt := ST1G;
					speed_cnt := speed_cnt + 1;            -----
				elsif speed_cnt = 40 then                -----
					speed_cnt := 0;                        -----    
					ball_speed := ball_speed - 1500000; 
					paddle_speed := paddle_speed - 1500000;   -----
					if ball_speed <= 1000000 then          -----
						ball_speed := 1000000;               -----
					end if;               
					if paddle_speed <= 1000000 then
					   paddle_speed := 1000000;
					end if;                 -----
				else
					nxt := SSlowClk;
				end if;
			-- ==================================================== UPDATE BALL CODE ====
			elsif cur = SClearBall then -- Clears where the ball used to be
			  x := Ballx;
			  y := Bally;
			  Ballx := Ballx + dx;
			  Bally := Bally + dy;
			  nxt := SDrawBall;
			  plot <= '1';
			  colour <= "000";

			  -- hit boundaries
        if Bally = Ymax-1 then
          dy := -1;
        elsif Bally = Ymin+1 then
          dy := 1;
        end if;
        -- hit a paddle
        if dx > 0 then
        	if Ballx = T1GX-1 then
        		if (Bally >= T1Gtop-1 and Bally <= T1Gbot+1) then
        			dx := -1;
        		end if;
        	elsif Ballx = T1FX-1 then
        		if (Bally >= T1Ftop-1 and Bally <= T1Fbot+1) then
        			dx := -1;
        		end if;
        	 elsif Ballx = T2FX-1 then
        		if (Bally >= T2Ftop-1 and Bally <= T2Fbot+1) then-- or (dy = 1 and Bally = T2Ftop-1) or (dy = -1 and Bally = T2fbot-1)) then
        			dx := -1;
        		end if;
        	elsif Ballx = T2GX-1 then
        		if (Bally >= T2Gtop-1 and Bally <= T2Gbot+1) then
        			dx := -1;
        		end if;
        	end if;
        elsif dx < 0 then --(hit back of paddle)
        	if Ballx = T1GX+1 then
        		if (Bally >= T1Gtop-1 and Bally <= T1Gbot+1) then
        			dx := 1;
        		end if;
        	elsif Ballx = T1FX+1 then
        		if (Bally >= T1Ftop-1 and Bally <= T1Fbot+1) then
        			dx := 1;
        		end if;
        	 elsif Ballx = T2FX+1 then
        		if (Bally >= T2Ftop-1 and Bally <= T2Fbot+1) then
        			dx := 1;
        		end if;
        	elsif Ballx = T2GX+1 then
        		if (Bally >= T2Gtop-1 and Bally <= T2Gbot+1) then
        			dx := 1;
        		end if;
        	end if; 
        end if;
        
        if Ballx = Xmax then
          nxt := SWait;
        elsif Ballx = Xmin then
          nxt := SWait;
        end if;
			   
			elsif cur = SDrawBall then -- Draws ball at new location
			  x := Ballx;
			  y := Bally;
			  nxt := SSlowClk;
			  plot <= '1';
			  colour <= "111";

			  ---- hit boundaries
     --   if Bally = Ymax-1 then
     --     dy := -1;
     --   elsif Bally = Ymin+1 then
     --     dy := 1;
     --   end if;
     --   -- hit a paddle
     --   if dx > 0 then
     --   	if Ballx = T1GX-1 then
     --   		if (Bally >= T1Gtop and Bally <= T1Gbot) then
     --   			dx := -1;
     --   		end if;
     --   	elsif Ballx = T1FX-1 then
     --   		if (Bally >= T1Ftop and Bally <= T1Fbot) then
     --   			dx := -1;
     --   		end if;
     --   	 elsif Ballx = T2FX-1 then
     --   		if (Bally >= T2Ftop and Bally <= T2Fbot) then-- or (dy = 1 and Bally = T2Ftop-1) or (dy = -1 and Bally = T2fbot-1)) then
     --   			dx := -1;
     --   		end if;
     --   	elsif Ballx = T2GX-1 then
     --   		if (Bally >= T2Gtop and Bally <= T2Gbot) then
     --   			dx := -1;
     --   		end if;
     --   	end if;
     --   elsif dx < 0 then --(hit back of paddle)
     --   	if Ballx = T1GX+1 then
     --   		if (Bally >= T1Gtop and Bally <= T1Gbot) then
     --   			dx := 1;
     --   		end if;
     --   	elsif Ballx = T1FX+1 then
     --   		if (Bally >= T1Ftop and Bally <= T1Fbot) then
     --   			dx := 1;
     --   		end if;
     --   	 elsif Ballx = T2FX+1 then
     --   		if (Bally >= T2Ftop and Bally <= T2Fbot) then
     --   			dx := 1;
     --   		end if;
     --   	elsif Ballx = T2GX+1 then
     --   		if (Bally >= T2Gtop and Bally <= T2Gbot) then
     --   			dx := 1;
     --   		end if;
     --   	end if; 
     --   end if;
        
     --   if Ballx = Xmax then
     --     nxt := SWait;
     --   elsif Ballx = Xmin then
     --     nxt := SWait;
     --   end if;
			-- ======================================================= UPDATE TEAM 1 GOALIE PADDLE =======================================
			elsif cur = ST1G then
				plot <= '0';
				x := T1GX;
				-- update first pixel in direction
				if prev = SSlowClk then
					-- capture direction
					dir := sw(17);
					-- going down
					if dir = '0' then
						if T1Gbot < Ymax-1 then
							T1Gbot := T1Gbot + 1;
							y := T1Gbot;
							plot <= '1';
							colour <= "001";
							nxt := ST1G;
						-- cant go down anymore
						else
							nxt := ST1F;
						end if;
					-- going up
					else
						if T1Gtop > Ymin+1 then
							T1Gtop := T1Gtop - 1;
							y := T1Gtop;
							plot <= '1';
							colour <= "001";
							nxt := ST1G;
						-- cant go up anymore
						else
							nxt := ST1F;
						end if;
					end if;
				-- update second pixel in direction
				elsif prev = ST1G then
					plot <= '1';
					colour <= "000";
					-- going down
					if dir = '0' then
						y := T1Gtop;
						T1Gtop := T1Gtop + 1;
					-- going up
					else
						y := T1Gbot;
						T1Gbot := T1Gbot - 1;
					end if;
					nxt := ST1F;
				end if;
			-- ======================================================= UPDATE TEAM 1 FORWARD PADDLE =======================================
			elsif cur = ST1F then
				x := T1FX;
				plot <= '0';
				-- update first pixel in direction
				if prev = ST1G then
					-- capture direction
					dir := sw(16);
					-- going down
					if dir = '0' then
						if T1Fbot < Ymax-1 then
							T1Fbot := T1Fbot + 1;
							y := T1Fbot;
							plot <= '1';
							colour <= "001";
							nxt := ST1F;
						-- cant go down anymore
						else
							nxt := ST2F;
						end if;
					-- going up
					else
						if T1Ftop > Ymin+1 then
							T1Ftop := T1Ftop - 1;
							y := T1Ftop;
							plot <= '1';
							colour <= "001";
							nxt := ST1F;
						-- cant go up anymore
						else
							nxt := ST2F;
						end if;
					end if;
				-- update second pixel in direction
				elsif prev = ST1F then
					plot <= '1';
					colour <= "000";
					-- going down
					if dir = '0' then
						y := T1Ftop;
						T1Ftop := T1Ftop + 1;
					-- going up
					else
						y := T1Fbot;
						T1Fbot := T1Fbot - 1;
					end if;
					nxt := ST2F;
				end if;

			-- ======================================================= UPDATE TEAM 2 FORWARD PADDLE =======================================
			elsif cur = ST2F then
				x := T2FX;
				plot <= '0';
				-- update first pixel in direction
				if prev = ST1F then
					-- capture direction
					dir := sw(1);
					-- going down
					if dir = '0' then
						if T2Fbot < Ymax-1 then
							T2Fbot := T2Fbot + 1;
							y := T2Fbot;
							plot <= '1';
							colour <= "100";
							nxt := ST2F;
						-- cant go down anymore
						else
							nxt := ST2G;
						end if;
					-- going up
					else
						if T2Ftop > Ymin+1 then
							T2Ftop := T2Ftop - 1;
							y := T2Ftop;
							plot <= '1';
							colour <= "100";
							nxt := ST2F;
						-- cant go up anymore
						else
							nxt := ST2G;
						end if;
					end if;
				-- update second pixel in direction
				elsif prev = ST2F then
					-- going down
					plot <= '1';
					colour <= "000";
					if dir = '0' then
						y := T2Ftop;
						T2Ftop := T2Ftop + 1;
					-- going up
					else
						y := T2Fbot;
						T2Fbot := T2Fbot - 1;
					end if;
					nxt := ST2G;
				end if;

			-- ======================================================= UPDATE TEAM 2 GOALIE PADDLE =======================================
			elsif cur = ST2G then
				x := T2GX;
				plot <= '0';
				-- update first pixel in direction
				if prev = ST2F then

					-- capture direction
					dir := sw(0);
					-- going down
					if dir = '0' then
						if T2Gbot < Ymax-1 then
							T2Gbot := T2Gbot + 1;
							y := T2Gbot;
							plot <= '1';
							colour <= "100";
							nxt := ST2G;
						-- cant go down anymore
						else
							nxt := SSlowClk;
						end if;
					-- going up
					else
						if T2Gtop > Ymin+1 then
							T2Gtop := T2Gtop - 1;
							y := T2Gtop;
							plot <= '1';
							colour <= "100";
							nxt := ST2G;
						-- cant go up anymore
						else
							nxt := SSlowClk;
						end if;
					end if;
				-- update second pixel in direction
				elsif prev = ST2G then
					plot <= '1';
					colour <= "000";
					-- going down
					if dir = '0' then
						y := T2Gtop;
						T2Gtop := T2Gtop + 1;
					-- going up
					else
						y := T2Gbot;
						T2Gbot := T2Gbot - 1;
					end if;
					nxt := SSlowClk;
				end if;

			elsif cur = SWait then
				plot <= '0';
				nxt := SWait;
			end if;

		 	Xcap := x;
	    Ycap := y;
	    if x < 0 then
	      Xcap := 0;
	    elsif x > 159 then
	      Xcap := 159;
	    end if;
	    if y < 0 then
	      Ycap := 0;
	    elsif y > 119 then
	      Ycap := 119;
	    end if;

	    prev := cur;
	    cur := nxt;

	    xcoord <= std_logic_vector(to_unsigned(Xcap, xcoord'length));
	    ycoord <= std_logic_vector(to_unsigned(Ycap, ycoord'length));

	    -- testing signals
	   	Tnxt <= nxt;

	  end if;
	end process;


end impl;