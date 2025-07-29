-- BizHawk Lua Script for Contra Final Score Capture
-- Monitors Player 1's lives and captures final score when lives reach zero
-- Author: Jeremy Stevens
-- Date: July 29, 2025

-- Memory addresses for Contra (NES) - From official RAM map
local PLAYER1_LIVES_ADDR = 0x0032       -- P1 Number Lives (0x00 is last life)
local PLAYER1_GAME_OVER_ADDR = 0x0038   -- P1 Game Over Status (0x00 not game over, 0x01 game over)

-- Player 1 Score addresses: 0x07E2–0x07E3 (2 bytes, little-endian, raw binary ×100)
local PLAYER1_SCORE_ADDR_LOW = 0x07E2   -- Low byte (little-endian)
local PLAYER1_SCORE_ADDR_HIGH = 0x07E3  -- High byte (little-endian)

-- State tracking variables
local previous_lives = -1
local score_captured = false
local last_capture_frame = -1000  -- Initialize to allow first capture
local capture_cooldown = 120  -- 2 seconds at 60 FPS to prevent duplicates
local game_over_frame = 0     -- Frame when game over was first detected
local capture_delay = 10      -- Frames to wait after game over before capturing
local cheats_detected = false
local awaiting_initials = false  -- Flag to indicate we're waiting for player initials
local player_initials = ""       -- Store the entered initials



-- Logging
local log_file = nil
local script_start_time = os.time()

-- Initialize logging
local function init_logging()
    local timestamp = os.date("%Y%m%d_%H%M%S")
    local filename = string.format("contra_scores_%s.txt", timestamp)
    log_file = io.open(filename, "w")
    if log_file then
        log_file:write(string.format("Contra Score Capture Log - Started: %s\n", os.date("%Y-%m-%d %H:%M:%S")))
        log_file:write("=" .. string.rep("=", 50) .. "\n")
        log_file:flush()
        console.log("Score logging initialized: " .. filename)
    else
        console.log("Warning: Could not create log file")
    end
end

-- Read Player 1's current lives
local function read_player1_lives()
    return memory.read_u8(PLAYER1_LIVES_ADDR)
end

-- Read Player 1's game over status
local function read_player1_game_over_status()
    return memory.read_u8(PLAYER1_GAME_OVER_ADDR)
end

-- Read Player 1's current score (2 bytes, little-endian, raw binary ×100)
local function read_player1_score()
    local low = memory.read_u8(PLAYER1_SCORE_ADDR_LOW)   -- Low byte
    local high = memory.read_u8(PLAYER1_SCORE_ADDR_HIGH) -- High byte
    
    -- Combine little-endian 16-bit value and multiply by 100 for display score
    local raw_score = low + (high * 256)  -- Little-endian: low byte + (high byte << 8)
    local display_score = raw_score * 100
    
    return display_score
end

-- Check for Game Genie cheat codes based on specific memory addresses
local function detect_cheats()
    -- Game Genie cheat addresses and their activated values
    local genie_cheats = {
        -- Lives cheats
        {addr = 0xDA03, value = 0xB5, name = "Infinite Lives"},
        {addr = 0xDA03, value = 0xA5, name = "Infinite Lives (Alt)"},
        {addr = 0xDA03, value = 0xF7, name = "Extra Life on Death"},
        {addr = 0xC468, value = 0x63, name = "30 Lives"},

        {addr = 0xC462, value = 0x1D, name = "P1+P2 30 Lives"},
        {addr = 0xC462, value = 0x9E, name = "175 Lives"},
        
        -- Weapon cheats
        {addr = 0xDAD3, value = 0x2C, name = "Keep Weapon"},
        {addr = 0xDAD2, value = 0x01, name = "Start with Machine Gun"},
        {addr = 0xDAD2, value = 0x02, name = "Start with Flame Thrower"},
        {addr = 0xDAD2, value = 0x03, name = "Start with Spread Gun"},
        {addr = 0xDAD2, value = 0x04, name = "Start with Laser"},
        
        -- Invincibility cheats
        {addr = 0xD467, value = 0xB5, name = "Invincibility"},
        {addr = 0xE2C9, value = 0xAD, name = "Alternate Invincible"},

        {addr = 0xD53D, value = 0xB0, name = "Super Body"},
        
        -- Movement cheats
        {addr = 0xD6E9, value = 0xFA, name = "Jump Higher"},
        {addr = 0xD9F0, value = 0x14, name = "Jump Higher 2"},
        {addr = 0xD476, value = 0x20, name = "Jump Mid Air 1"},
        {addr = 0xD477, value = 0x9F, name = "Jump Mid Air 2"},
        {addr = 0xD478, value = 0xD6, name = "Jump Mid Air 3"},
        {addr = 0xD479, value = 0xEA, name = "Jump Mid Air 4"},
        {addr = 0xD480, value = 0xB5, name = "Jump Mid Air 5"},
        {addr = 0xD9E9, value = 0xB5, name = "Jump Mid Air 6"},
        {addr = 0xD54A, value = 0x60, name = "Jump Mid Air 7"},
        {addr = 0xD75D, value = 0x04, name = "Run 4x Faster 1"},
        {addr = 0xD761, value = 0xFC, name = "Run 4x Faster 2"},

        {addr = 0xE01D, value = 0xB5, name = "Walk on Water"},
        
        -- Level/Game cheats (removed 0x00 checks that cause false positives)
        {addr = 0xC479, value = 0x30, name = "Level Select"},
        {addr = 0xD04D, value = 0x3B, name = "Press Start to Complete Level"},
        {addr = 0xCD5A, value = 0x30, name = "Turn Off Electric Barrier"},
        
        -- Combat cheats
        {addr = 0xD063, value = 0x98, name = "Harder Boss"},
        {addr = 0xE3F8, value = 0x94, name = "Bullets Through Enemies"},
        {addr = 0xE358, value = 0xA9, name = "Enemies Die Auto 1"},
        {addr = 0xE360, value = 0x42, name = "Enemies Die Auto 2"},

        {addr = 0xC4A7, value = 0xAD, name = "Tons of Points"},
        
        -- Visual/Audio cheats
        {addr = 0x8348, value = 0xD9, name = "Slow Weapons Capsules"},
        {addr = 0xC7C9, value = 0x98, name = "Walk on Exploded Bridge"},
        {addr = 0x88C4, value = 0xBD, name = "DPCM Pop Reducer 1"},
        {addr = 0xC07E, value = 0xA9, name = "Black and White Mode 1"},
        {addr = 0xC07F, value = 0x1F, name = "Black and White Mode 2"},
        {addr = 0xCEE0, value = 0x14, name = "Remove Lifebar Indicators"}
    }
    
    -- Check each Game Genie cheat address
    for i = 1, #genie_cheats do
        local cheat = genie_cheats[i]
        local memory_value = memory.read_u8(cheat.addr)
        
        if memory_value == cheat.value then
            return true, cheat.name .. " Code"
        end
    end
    
    -- Check for BizHawk cheat database active (but only if function exists)
    if client and client.getcheats then
        local success, cheats = pcall(client.getcheats)
        if success and cheats and #cheats > 0 then
            -- Check if any cheats are actually enabled, not just present
            for i = 1, #cheats do
                if cheats[i].enabled then
                    return true, "Emulator Cheat Active"
                end
            end
        end
    end
    
    -- Check for obvious infinite lives value (255)
    local lives = read_player1_lives()
    if lives == 255 then
        return true, "Infinite Lives (Memory)"
    end
    
    return false, ""
end

-- Format score without unnecessary leading zeros
local function format_score(score)
    -- Add commas for thousands separators
    local formatted = tostring(score)
    local result = ""
    local len = string.len(formatted)
    
    for i = 1, len do
        local digit = string.sub(formatted, i, i)
        result = result .. digit
        
        -- Add comma if there are more digits and position is right for comma
        local remaining = len - i
        if remaining > 0 and remaining % 3 == 0 then
            result = result .. ","
        end
    end
    
    return result
end

-- Prompt for player initials
local function prompt_for_initials()
    local initials = ""
    repeat
        initials = forms.gettext("Enter your initials (3 characters):", "Player Initials", "")
        if initials then
            initials = string.upper(string.sub(initials, 1, 3))  -- Convert to uppercase and limit to 3 chars
        end
    until initials and string.len(initials) >= 1 and string.len(initials) <= 3
    
    return initials
end

-- Log captured score with player initials
local function log_score(score)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    local formatted_score = format_score(score)
    
    -- Get player initials
    if not awaiting_initials then
        awaiting_initials = true
        player_initials = prompt_for_initials()
        awaiting_initials = false
    end
    
    local log_entry = string.format("[%s] Player: %s - Final Score: %s", timestamp, player_initials, formatted_score)
    
    -- Console output
    console.log("=" .. string.rep("=", 50))
    console.log("GAME OVER - SCORE CAPTURED!")
    console.log("Player: " .. player_initials)
    console.log("Final Score: " .. formatted_score)
    console.log("Time: " .. timestamp)
    console.log("=" .. string.rep("=", 50))
    
    -- File logging
    if log_file then
        log_file:write(log_entry .. "\n")
        log_file:flush()
    end
    
    -- Reset initials for next game
    player_initials = ""
end

-- Check if we're in a valid game state
local function is_valid_game_state()
    -- Basic validation - make sure we're not in menu or other non-game states
    local lives = read_player1_lives()
    return lives >= 0 and lives <= 10  -- Reasonable range for lives
end

-- Main monitoring function
local function monitor_game_state()
    if not is_valid_game_state() then
        return
    end
    
    -- Check for cheats first
    local cheat_found, cheat_type = detect_cheats()
    if cheat_found and not cheats_detected then
        cheats_detected = true
        console.log("CHEATS DETECTED: " .. cheat_type .. " - Score tracking disabled")
    elseif not cheat_found and cheats_detected then
        cheats_detected = false
        console.log("Cheats no longer detected - Score tracking re-enabled")
    end
    
    local current_lives = read_player1_lives()
    local current_frame = emu.framecount()
    
    -- Check if we need to reset capture state (new game started)
    if current_lives > 0 and score_captured then
        score_captured = false
        game_over_frame = 0
        console.log("New game detected - ready to capture next final score")
    end
    
    local game_over_status = read_player1_game_over_status()
    

    
    -- Detect game over using both lives count and game over status flag
    if game_over_status == 1 and not score_captured then
        -- Mark the frame when game over was first detected
        if game_over_frame == 0 then
            game_over_frame = current_frame
            if not cheats_detected then
                console.log("Game over detected - waiting for score to stabilize...")
            else
                console.log("Game over detected - but cheats are active, score will not be tracked")
            end
        end
        
        -- Only capture score if no cheats detected
        if not cheats_detected then
            -- Wait for the score to stabilize, then capture
            if current_frame - game_over_frame >= capture_delay then
                if current_frame - last_capture_frame > capture_cooldown then
                    local final_score = read_player1_score()
                    
                    -- Validate score (basic sanity check)
                    if final_score >= 0 and final_score <= 99999999 then
                        log_score(final_score)
                        score_captured = true
                        last_capture_frame = current_frame
                    else
                        console.log(string.format("Warning: Invalid score detected (%d), skipping capture", final_score))
                    end
                end
            end
        else
            -- Mark as captured to prevent repeated messages
            score_captured = true
        end
    end
    
    -- Update previous state
    previous_lives = current_lives
end

-- Display player's score or cheat warning
local function display_score_only()
    if cheats_detected then
        gui.text(10, 10, "Cheats are enabled", "red", "black")
        gui.text(10, 25, "Score keeping is disabled", "orange", "black")
    elseif awaiting_initials then
        gui.text(10, 10, "Enter your initials", "yellow", "black")
        gui.text(10, 25, "in the dialog box", "white", "black")
    else
        local score = read_player1_score()
        gui.text(10, 10, string.format("Score: %s", format_score(score)), "white", "black")
    end
end

-- Cleanup function
local function cleanup()
    if log_file then
        log_file:write(string.format("\nScript ended: %s\n", os.date("%Y-%m-%d %H:%M:%S")))
        log_file:close()
        console.log("Log file closed")
    end
end

-- Initialize script
local function init_script()
    console.clear()
    console.log("Contra Final Score Capture Script Started")
    console.log("Monitoring Player 1 for game over...")
    console.log("Memory addresses:")
    console.log(string.format("  Lives: 0x%04X", PLAYER1_LIVES_ADDR))
    console.log(string.format("  Score: 0x%04X-0x%04X (2 bytes little-endian × 100)", PLAYER1_SCORE_ADDR_LOW, PLAYER1_SCORE_ADDR_HIGH))
    console.log("Ready to capture final scores!")
    
    init_logging()
end

-- Register event handlers
event.onexit(cleanup)

-- Main execution
init_script()

-- Main loop - this function is called every frame
while true do
    monitor_game_state()
    display_score_only()
    emu.frameadvance()
end
