Material blackMat = new Material(MaterialType.DIFFUSE, new Color(0, 0, 0), null, -1, -1, -1);

enum MaterialType {
  GLOSSY, DIFFUSE
}

class Material {
  public MaterialType type;
  public Color diffuseColor;
  public Color specularColor;
  public float specularPow;
  public float kRefl;
  public float glossRadius;
  
  Material(MaterialType type, Color diffuseColor, Color specularColor,
           float specularPow, float kRefl, float glossRadius) {
    this.type = type;
    this.diffuseColor = diffuseColor;
    this.specularColor = specularColor;
    this.specularPow = specularPow;
    this.kRefl = kRefl;
    this.glossRadius = glossRadius;
  }

}
