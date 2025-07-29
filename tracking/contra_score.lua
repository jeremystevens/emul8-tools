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

-- Format score with proper spacing
local function format_score(score)
    return string.format("%08d", score)
end

-- Log captured score
local function log_score(score)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    local formatted_score = format_score(score)
    local log_entry = string.format("[%s] Final Score: %s", timestamp, formatted_score)
    
    -- Console output
    console.log("=" .. string.rep("=", 40))
    console.log("GAME OVER - SCORE CAPTURED!")
    console.log("Player 1 Final Score: " .. formatted_score)
    console.log("Time: " .. timestamp)
    console.log("=" .. string.rep("=", 40))
    
    -- File logging
    if log_file then
        log_file:write(log_entry .. "\n")
        log_file:flush()
    end
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
            console.log("Game over detected - waiting for score to stabilize...")
        end
        
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
    end
    
    -- Update previous state
    previous_lives = current_lives
end

-- Display current game state (optional debug info)
local function display_debug_info()
    local lives = read_player1_lives()
    local game_over_status = read_player1_game_over_status()
    local score = read_player1_score()
    local current_frame = emu.framecount()
    
    gui.text(10, 10, string.format("P1 Lives: %d", lives), "white", "black")
    gui.text(10, 25, string.format("Game Over: %s", game_over_status == 1 and "YES" or "NO"), 
             game_over_status == 1 and "red" or "white", "black")
    gui.text(10, 40, string.format("P1 Score: %s", format_score(score)), "white", "black")
    gui.text(10, 55, string.format("Captured: %s", score_captured and "YES" or "NO"), 
             score_captured and "lime" or "yellow", "black")
    
    -- Show timing info when game over is detected
    if game_over_frame > 0 and not score_captured then
        local wait_frames = capture_delay - (current_frame - game_over_frame)
        if wait_frames > 0 then
            gui.text(10, 70, string.format("Capturing in: %d frames", wait_frames), "orange", "black")
        else
            gui.text(10, 70, "Ready to capture!", "lime", "black")
        end
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
    display_debug_info()
    emu.frameadvance()
end
