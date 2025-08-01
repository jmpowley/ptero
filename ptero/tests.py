def validate_velocity_intervals(self, vmin, vmax, vstep):
        if vmin >= vmax:
            return "vmin must be less than vmax."
        if vmin % 25 != 0 or vmax % 25 != 0:
            return "vmin and vmax must be multiples of 25."
        if vstep % 25 != 0:
            return "vstep must be a multiple of 25."
        return None