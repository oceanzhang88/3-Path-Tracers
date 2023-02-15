class NamedObject {
  protected HashMap<String, SceneObject> map;
  
  NamedObject() {
    map = new HashMap<String, SceneObject>();
  }
}

class Instance extends SceneObject implements HitTest {
  public ArrayList<Matrix> C;
  public ArrayList<Matrix> CInv;
  public ArrayList<Matrix> CInvT;
  public SceneObject object;
  private Ray instray;
  
  Instance(ArrayList<Matrix> C, SceneObject object) {
    this.C = new ArrayList<Matrix>(C);
    this.object = object;
    this.CInv = new ArrayList<Matrix>();
    this.CInvT = new ArrayList<Matrix>();
    
    for (int i = 0; i < C.size(); i++) {
      Matrix mat = C.get(i);
      Matrix matInv = null;
      switch (mat.type) {
        case TRANSLATE:
          matInv = translateMTInv(mat);
          CInv.add(matInv);
          CInvT.add(transposeMT(matInv));
          break;
        case ROTATE:
          matInv = rotateMTInv(mat);
          CInv.add(matInv);
          CInvT.add(transposeMT(matInv));
          break;
        case SCALE:
          matInv = scaleMTInv(mat);
          CInv.add(matInv);
          CInvT.add(transposeMT(matInv));
          break;
        case IDENTITY:
          CInv.add(identityMT());
          CInvT.add(identityMT());
          break;
      }
    }
  }
  
  public Hit isHit(Ray ray){
    instray = new Ray(ray.shadowRay);
    instray.origin = ray.origin;
    instray.dir = ray.dir;
    //if (debug_flag && ray.shadowRay) {
    //  print("!");
    //}
    HitTest ht  = getHitTest(object);
    for (int i = 0; i < CInv.size(); i++) {
      Matrix mat = CInv.get(i);
      instray.dir = mat.mult(instray.dir);
      instray.origin = mat.mult(instray.origin);
    }
    Hit hit = ht.isHit(instray);
    if (hit == null) {
      return null;
    }
    
    for (int i = C.size() - 1; i >= 0; i--) {
      Matrix mat = C.get(i);
      hit.p = mat.mult(hit.p);
      
      Matrix matInvT = CInvT.get(i);
      hit.normal = matInvT.mult(hit.normal);
    }
   
    hit.normal.normalize();
    hit.ray = ray;
    return hit;
  }
}
