class Ray:
    def cast_ray(spheres, ray_origin, ray_direction):
        """ Cast a ray and find closest sphere """
        closest_t = float("inf")
        closest_sphere = None

        for sphere in spheres:
            t = sphere.intersects(ray_origin, ray_direction)
            if t and t < closest_t:
                closest_t = t
                closest_sphere = sphere

        return closest_sphere, closest_t