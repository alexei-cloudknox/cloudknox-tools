package fix

import scalafix.v1._

import scala.meta._
import scala.meta.contrib.XtensionTreeOps

class AddContextVarV1 extends SemanticRule("AddContextVarV1") {
  final override val description: String = "Adds Context as a first argument to cloudknox classes"

  final val contextStr = "context: BaseContext"
  final val contextImport = "import io.cloudknox.models.common.BaseContext"
  final val contextToMarkerImplicit = s"${contextImport}._"
  //final val contextImport ="import scala.Int"
  //final val contextToMarkerImplicit = "import scala.Boolean"

  override def fix(implicit doc: SemanticDocument): Patch = {
    val tree = doc.tree
    tree.collect {
      case t : Pkg =>
        // Found package declaration. Add imports right after package name
        t.children.zipWithIndex
          .collect{
            case (c, 1) =>
              Patch.addLeft(c, s"$contextImport\n$contextToMarkerImplicit\n").atomic
          }
          .asPatch

      case t : Decl.Def if t.paramss.isEmpty =>
        // no parameters in the function, declaration does not ()
        Patch.addRight(t.name.tokens.last, s"(implicit $contextStr)").atomic

      case t : Decl.Def if t.paramss.last.isEmpty =>
        // no parameters in the function, but declaration has empty ()

        if (t.decltpe.tokens.isEmpty) {
          // No patch: declaration without return type
          Patch.empty
        } else {
          val p = t.decltpe.tokens.head.start
          t.tokens.filter{ tl => tl.is[Token.RightParen] && tl.start < p}
            .lastOption
            .map(
              Patch.addRight(_, s"(implicit $contextStr)").atomic
            )
            .getOrElse(Patch.empty)
        }

      case t : Decl.Def if t.paramss.last.exists(_.mods.exists(_.is[Mod.Implicit])) =>
        // function already have implicit params
        if (t.decltpe.tokens.isEmpty)
          Patch.addLeft(t.tokens.last, s", $contextStr")
        else
          t.tokens.filter(_.is[Token.RightParen])
            .lastOption
            .map(
              Patch.replaceToken(_, s", $contextStr)").atomic
            )
            .getOrElse(Patch.empty)

      case t : Decl.Def =>
        // Function with param, but no implicits
        if (t.decltpe.tokens.isEmpty)
          Patch.addRight(t.tokens.last, s"(implicit $contextStr)")
        else
          t.tokens.filter(_.is[Token.Colon])
            .lastOption
            .map (
              Patch.addLeft(_, s"(implicit $contextStr)").atomic
            )
            .getOrElse(Patch.empty)

        // ++++++++++++++++  Defn

      case t : Defn.Def if t.paramss.isEmpty =>
        // no parameters in the function, declaration does not ()
        Patch.addRight(t.name.tokens.last, s"(implicit $contextStr)").atomic

      case t : Defn.Def if t.paramss.last.isEmpty =>
        // no parameters in the function, but declaration has empty ()
        t.children.find(_.is[Term.Block])
          .map{ tl =>
            val blockPos = tl.tokens.head.start
            t.tokens
              .filter{ t =>
                val v = t.is[Token.RightParen] && t.end < blockPos
                v
              }
              .lastOption
              .map(
                Patch.addRight(_, s"(implicit $contextStr)").atomic
              )
              .getOrElse(
                Patch.empty
              )
          }
          .getOrElse(Patch.empty)

      case t : Defn.Def if t.paramss.last.exists(_.mods.exists(_.is[Mod.Implicit])) =>
        t.children.filter(_.is[Term.Param])
          .lastOption
          .map(
            Patch.addRight(_, s", $contextStr")
          )
          .getOrElse(
            Patch.empty
          )

      case t : Defn.Def =>
        t.children.filter(_.is[Term.Param])
          .lastOption
          .map{ ip =>
            t.tokens
              .find{ t => t.is[Token.RightParen] && t.end > ip.tokens.last.end}
              .map(
                Patch.addRight(_, s"(implicit $contextStr)")
              )
              .getOrElse(
                Patch.empty
              )
          }
          .getOrElse(
            t.children.filter(_.is[Term.Name])
              .lastOption
              .map{ name =>
                Patch.addRight(name, s"(implicit $contextStr)")
              }
              .getOrElse(
                Patch.empty
              )
          )
    }
      .asPatch
  }
/*
        val v1 = t.paramss
        val v2 = t.tokens
        val v3 = t.decltpe
        val v4 = t.children
        val v4a = v4.head.tokens
        val v5 = t.mods
        val v6 = t.tparams
        val v7 = t.name
        val v7a = v7.tokens
 */
}
