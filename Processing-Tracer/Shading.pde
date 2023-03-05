class Color {
  public float r;
  public float g;
  public float b;

  Color(float r, float g, float b) {
    this.r = r;
    this.g = g;
    this.b = b;
  }

  @Override
    public String toString() {
    return "color: " + this.r + " " + this.g + " " + this.b;
  }
}

class Shader {
  
  public Color getGlobalIllumination(Ray ray, int depth) {
    //Find direct illumination color
    Hit hit = scene.castRay(ray);
    
    if (hit != null) {
      Color out = new Color(0, 0, 0);
      // set the pixel color, you should put the correct pixel color here
      Color direct = getDirectIllumination(scene.lights, hit);
      out = colorAdd(out, direct); 
      
      Material mat = hit.material;
      //Find reflection color
      if (mat.kRefl > 0 && depth < recDepth) {
        PVector reflDir = getReflDir(hit.normal, hit.ray.dir);
        if (mat.glossRadius > 0) {
          reflDir = sample(reflDir, mat.glossRadius);
        }
        Ray reflRay = new Ray(hit.p, reflDir, false, -1);
        
        Color reflColor = getGlobalIllumination(reflRay, depth + 1);
        reflColor = colorMul(reflColor, mat.kRefl);
        out = colorAdd(out, reflColor);
      }  
      return out;
    } 
    
    return scene.bkColor;
  }
  
  public Color getDirectIllumination(ArrayList<Light> lights, Hit hit) {
    int i = 0;
    Point p = hit.p;
    Color out = new Color(0, 0, 0);
    
    for(Light light : lights) {
      i++;
      
      Color lightColor = light.lcolor();
      Point lcenter = light.center();
      PVector l = null;
      
      if (light instanceof SpotLight) {
        //We only 2 kinds of light, directional and spot
        SpotLight slight = (SpotLight)light;
        lcenter = slight.sample();
      }
      
      l = new PVector(lcenter.x - p.x, lcenter.y - p.y, lcenter.z - p.z);
      l.normalize();
      
      if (scene.isOcculuded(hit, lcenter)) {
        continue;
      }
      
      PVector n = hit.normal;
      PVector vDir = hit.ray.dir.copy();
      vDir.normalize();
      vDir.mult(-1); //align with normal orientation
      
      PVector h = vDir.add(l);
      h.normalize();
      
      Material objMaterial = hit.material;
      
      Color objDiffuse = objMaterial.diffuseColor;
      Color objSpecular = new Color(0, 0, 0);
      
      if (objMaterial.specularPow > 0){
        objSpecular = objMaterial.specularColor;
  
        float ndoth = Math.max(0, n.dot(h));
        float specPow = (float)Math.pow(ndoth, objMaterial.specularPow);
        
        objSpecular = colorBlend(objSpecular, lightColor);
        objSpecular = colorMul(objSpecular, specPow);
      }
      
      float ndotl = Math.max(0, n.dot(l));
      Color albedo = colorBlend(objDiffuse, lightColor);
      Color diffuse = colorMul(albedo, ndotl);
      
      //if (debug_flag) {
      //    println("debug ray occuluded from light:", i);
      //}
      out = colorAdd(out, diffuse);
      out = colorAdd(out, objSpecular);
    }
    
    return out;
  }
  
  private PVector sample(PVector dir, float radius) {
    while (true) {
      float x = random(-radius, radius);
      float y = random(-radius, radius);
      float z = random(-radius, radius);
      
      float distSqure = x * x + y * y + z * z;
  
      if (distSqure <= radius * radius) {
        float dx = dir.x + x;
        float dy = dir.y + y;
        float dz = dir.z + z;
        PVector newDir = new PVector(dx, dy, dz);
        newDir.normalize();
        return newDir;
      }
    }
  }
  
  private PVector getReflDir(PVector n, PVector v) {
    PVector vnorm = v.copy();
    PVector nnorm = n.copy();
    vnorm.normalize();
    nnorm.normalize();
    
    float ndotv = nnorm.dot(vnorm);
    PVector n2ndotv = nnorm.mult(2 * ndotv);
    PVector rnorm = vnorm.sub(n2ndotv);
    rnorm.normalize();
    return rnorm;
  }
}
