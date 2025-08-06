import asyncio
from src.infrastructure.implementation.configuration.yaml_configuration import YamlConfiguration
from src.domain.value_objects.test_configuration import TestConfiguration

async def verify_synchronization():
    # Create YamlConfiguration instance
    yaml_config = YamlConfiguration()
    
    # Create original configuration
    original_config = TestConfiguration()
    
    # Load from regenerated YAML file
    loaded_config = await yaml_config.load_profile('default')
    
    # Compare key fields to verify synchronization
    fields_to_check = [
        'voltage', 'current', 'upper_current', 'upper_temperature',
        'activation_temperature', 'standby_temperature', 'fan_speed',
        'velocity', 'acceleration', 'deceleration',
        'stabilization_delay', 'temperature_stabilization', 'standby_stabilization',
        'max_velocity', 'max_acceleration', 'max_deceleration'
    ]
    
    all_match = True
    for field in fields_to_check:
        original_value = getattr(original_config, field)
        loaded_value = getattr(loaded_config, field)
        if original_value \!= loaded_value:
            print(f'MISMATCH: {field} - original: {original_value}, loaded: {loaded_value}')
            all_match = False
        else:
            print(f'✓ {field}: {original_value}')
    
    if all_match:
        print('')
        print('✅ All fields match\! TestConfiguration and YAML are synchronized.')
    else:
        print('')
        print('❌ Some fields do not match.')
        
    # Test that the loaded config is valid
    if loaded_config.is_valid():
        print('✅ Loaded configuration is valid.')
    else:
        print('❌ Loaded configuration is invalid.')

# Run the verification
asyncio.run(verify_synchronization())
EOF < /dev/null
