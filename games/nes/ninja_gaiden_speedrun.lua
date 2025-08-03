-- Ninja Gaiden Speedrun Timer
-- Author: Jeremy Stevens
-- For use with Bizhawk
-- Version 1.0

local prevStage = nil
local stageStartFrame = emu.framecount()
local output = io.open("ninja_gaiden_times.txt", "a")

while true do
    local currentStage = memory.read_u8(0x006D)
    local currentRoom  = memory.read_u8(0x006E)
    local timer        = memory.read_u8(0x0063)
    local frameCounter = emu.framecount()
    local framesInStage = frameCounter - stageStartFrame
    local totalSeconds = framesInStage / 60
    local minutes = math.floor(totalSeconds / 60)
    local seconds = math.floor(totalSeconds % 60)

    -- On-screen debug info
    gui.text(5, 10, "Stage: " .. currentStage)
    gui.text(5, 25, "Room: " .. currentRoom)
    gui.text(5, 40, "Time Left: " .. timer)
    gui.text(5, 55, "Frames in Stage: " .. framesInStage)
    gui.text(5, 70, string.format("Time: %d:%02d", minutes, seconds))

    -- Log on stage change
    if prevStage and currentStage ~= prevStage then
        if prevStage > 0 and prevStage < 7 and framesInStage > 100 then
            local line = string.format(
                "Stage %d   Time: %d frames (%d:%02d)\n",
                prevStage, framesInStage, minutes, seconds
            )
            output:write(line)
            output:flush()
        end
        stageStartFrame = frameCounter
    end

    prevStage = currentStage
    emu.frameadvance()
end
