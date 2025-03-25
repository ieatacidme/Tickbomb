import math
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Constants
AU_IN_M = 149597870700  # Astronomical Unit in meters

def calculate_time_in_warp(max_warp_speed, max_subwarp_speed, warp_dist):
    """
    Calculate the time and distance parameters for a warp in EVE Online.
    """
    k_accel = max_warp_speed
    k_decel = min(max_warp_speed / 3, 2)
    warp_dropout_speed = min(max_subwarp_speed / 2, 100)
    max_ms_warp_speed = max_warp_speed * AU_IN_M

    # Calculate acceleration time and distance
    accel_time = math.log(max_ms_warp_speed / k_accel) / k_accel
    accel_dist = (max_ms_warp_speed / k_accel) * (1 - math.exp(-k_accel * accel_time))

    # Calculate deceleration time and distance
    decel_time = math.log(max_ms_warp_speed / warp_dropout_speed) / k_decel
    decel_dist = (max_ms_warp_speed / k_decel) * (1 - math.exp(-k_decel * decel_time))

    # Calculate cruise distance and time
    minimum_dist = accel_dist + decel_dist
    cruise_dist = max(0, warp_dist - minimum_dist)
    cruise_time = cruise_dist / max_ms_warp_speed if max_ms_warp_speed > 0 else 0

    total_time = accel_time + cruise_time + decel_time
    
    return total_time, accel_time, cruise_time, decel_time, accel_dist, cruise_dist, decel_dist, k_accel, k_decel, max_ms_warp_speed

def calculate_distance_remaining(time_left, k_decel, max_ms_warp_speed, warp_dropout_speed, decel_dist):
    """
    Calculate how much distance will be covered in the remaining time
    """
    if time_left <= 0:
        return 0
    
    # Check if we're in deceleration phase for the entire remaining time
    if time_left >= math.log(max_ms_warp_speed / warp_dropout_speed) / k_decel:
        return decel_dist  # Shouldn't happen since we're calculating for the end of warp
    
    # Distance covered during deceleration phase
    distance = (max_ms_warp_speed / k_decel) * (1 - math.exp(-k_decel * time_left))
    return distance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get input values from form
        data = request.get_json()
        distance_au = float(data.get('distance', 1))
        distance_m = distance_au * AU_IN_M
        warp_speed = float(data.get('warp_speed', 5))
        subwarp_speed = float(data.get('subwarp_speed', 200))
        detonation_time = float(data.get('detonation_time', 5))
        
        # Validate inputs
        if distance_au <= 0 or warp_speed <= 0 or subwarp_speed <= 0 or detonation_time <= 0:
            return jsonify({'error': 'All values must be greater than zero.'})
        
        # Calculate warp parameters
        (total_time, accel_time, cruise_time, decel_time, 
         accel_dist, cruise_dist, decel_dist, 
         k_accel, k_decel, max_ms_warp_speed) = calculate_time_in_warp(warp_speed, subwarp_speed, distance_m)
        
        warp_dropout_speed = min(subwarp_speed / 2, 100)
        
        # Calculate distance that will be covered during the detonation time
        distance_during_detonation = calculate_distance_remaining(
            detonation_time, k_decel, max_ms_warp_speed, warp_dropout_speed, decel_dist)
        
        remaining_distance_at_launch = distance_during_detonation
        remaining_distance_au = remaining_distance_at_launch / AU_IN_M
        
        # Calculate when to launch (time when remaining distance equals distance covered in detonation time)
        launch_time = total_time - detonation_time
        
        # Calculate current speed at launch time
        if launch_time <= accel_time:
            current_speed = k_accel * AU_IN_M * math.exp(k_accel * launch_time)
        elif launch_time <= (accel_time + cruise_time):
            current_speed = warp_speed * AU_IN_M  # Max speed
        else:
            time_in_decel = launch_time - accel_time - cruise_time
            current_speed = warp_speed * AU_IN_M * math.exp(-k_decel * time_in_decel)
        
        # Format the results
        results = {
            'target_info': {
                'warp_distance': f"{distance_au:.2f} AU ({distance_m/1000:,.0f} km)",
                'warp_speed': f"{warp_speed} AU/s",
                'subwarp_speed': f"{subwarp_speed} m/s",
                'detonation_time': f"{detonation_time} seconds"
            },
            'warp_time': {
                'accel_phase': f"{accel_time:.2f} seconds (distance: {accel_dist/1000:,.0f} km)",
                'cruise_phase': f"{cruise_time:.2f} seconds (distance: {cruise_dist/1000:,.0f} km)",
                'decel_phase': f"{decel_time:.2f} seconds (distance: {decel_dist/1000:,.0f} km)",
                'total_time': f"{total_time:.2f} seconds"
            },
            'bomb_timing': {
                'launch_time': f"{launch_time:.2f} seconds after warp start",
                'time_before_landing': f"{detonation_time:.2f} seconds before landing",
                'distance_remaining': f"{remaining_distance_au:.4f} AU ({remaining_distance_at_launch/1000:,.0f} km)",
                'current_speed': f"{current_speed:,.0f} m/s ({current_speed/AU_IN_M:.2f} AU/s)"
            },
            'countdown': {
                'total_time': total_time,
                'launch_time': launch_time
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)